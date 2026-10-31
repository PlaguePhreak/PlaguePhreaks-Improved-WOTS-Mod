// Three-way merge of Assembly-CSharp.dll:
//   stock  = the original game DLL (only its fingerprint is needed),
//   mod    = PlaguePhreak's modded DLL,
//   target = the DLL the player has now (may already hold other DLL mods).
// Every type, field and method the mod added or changed (compared with stock) is copied
// into the target. Anything else in the target, including other mods' changes, stays.
// A conflict is a method (or type/field) that BOTH the mod and the target changed.
using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace WotsInstaller
{
    public class MergeReport
    {
        public List<string> Conflicts = new List<string>();
        public List<string> Notes = new List<string>();
        public int TypesAdded, TypesSkipped, MethodsReplaced, MethodsAdded, MethodsSame, FieldsAdded, TypesReplaced;
        public string Summary()
        {
            return string.Format("{0} new classes, {1} classes replaced, {2} game methods changed, {3} methods added, {4} fields added, {5} already identical, {6} conflicts",
                TypesAdded, TypesReplaced, MethodsReplaced, MethodsAdded, FieldsAdded, MethodsSame + TypesSkipped, Conflicts.Count);
        }
    }

    public class Merger
    {
        readonly ModuleDefinition target, mod;
        readonly StockFp stock;
        readonly MergeReport rep = new MergeReport();
        readonly Dictionary<string, TypeDefinition> tTypes = new Dictionary<string, TypeDefinition>();

        // planned work
        readonly List<TypeDefinition> addTypes = new List<TypeDefinition>();          // mod types to add (top of each added subtree)
        readonly List<TypeDefinition> replaceTypes = new List<TypeDefinition>();      // added types that clash with a different target type
        readonly List<KeyValuePair<MethodDefinition, MethodDefinition>> replaceBodies = new List<KeyValuePair<MethodDefinition, MethodDefinition>>(); // mod, target
        readonly List<MethodDefinition> addMethods = new List<MethodDefinition>();
        readonly List<FieldDefinition> addFields = new List<FieldDefinition>();
        readonly List<PropertyDefinition> addProps = new List<PropertyDefinition>();
        readonly List<EventDefinition> addEvents = new List<EventDefinition>();
        readonly List<KeyValuePair<TypeDefinition, TypeDefinition>> headerChanges = new List<KeyValuePair<TypeDefinition, TypeDefinition>>();
        bool planned;

        public Merger(ModuleDefinition target, ModuleDefinition mod, StockFp stock)
        {
            this.target = target; this.mod = mod; this.stock = stock;
        }

        public MergeReport Report { get { return rep; } }

        // ---------------------------------------------------------------- planning
        public MergeReport Plan()
        {
            if (planned) return rep;
            planned = true;
            foreach (var t in Fp.AllTypes(target)) tTypes[t.FullName] = t;

            foreach (var mt in mod.Types) PlanType(mt, false);
            return rep;
        }

        void PlanType(TypeDefinition mt, bool parentAdded)
        {
            if (parentAdded) return; // copied with its parent
            StockType st;
            stock.Types.TryGetValue(mt.FullName, out st);
            TypeDefinition tt;
            tTypes.TryGetValue(mt.FullName, out tt);

            if (st == null)
            {
                // the mod added this type
                if (tt == null) { addTypes.Add(mt); rep.TypesAdded++; }
                else if (Fp.TypeHash(tt) == Fp.TypeHash(mt)) rep.TypesSkipped++;
                else
                {
                    replaceTypes.Add(mt); rep.TypesReplaced++;
                    rep.Conflicts.Add("Class " + mt.FullName + " already exists in your game DLL with different code (another mod, or an older copy of this mod).");
                }
                return;
            }

            if (tt == null)
            {
                rep.Notes.Add("Game class " + mt.FullName + " is missing from your DLL; skipped.");
                return;
            }

            // header (flags / base type / interfaces)
            if (Fp.Hash(Fp.TypeHeader(mt)) != st.Header)
            {
                if (Fp.Hash(Fp.TypeHeader(tt)) == st.Header) headerChanges.Add(new KeyValuePair<TypeDefinition, TypeDefinition>(mt, tt));
                else if (Fp.TypeHeader(tt) != Fp.TypeHeader(mt))
                    rep.Notes.Add("Class header of " + mt.FullName + " was changed by another mod too; kept theirs.");
            }

            // fields
            var tFields = new Dictionary<string, FieldDefinition>();
            foreach (var f in tt.Fields) tFields[f.Name] = f;
            foreach (var f in mt.Fields)
            {
                if (st.Fields.ContainsKey(f.Name)) continue; // stock field (the mod never changes those)
                FieldDefinition tf;
                if (!tFields.TryGetValue(f.Name, out tf)) { addFields.Add(f); rep.FieldsAdded++; }
                else if (Fp.FieldText(tf) != Fp.FieldText(f))
                    rep.Conflicts.Add("Field " + mt.FullName + "." + f.Name + " exists in your DLL with a different type (" + tf.FieldType.FullName + ").");
            }

            // methods
            var tMethods = new Dictionary<string, MethodDefinition>();
            foreach (var m in tt.Methods) tMethods[Fp.MethodKey(m)] = m;
            foreach (var m in mt.Methods)
            {
                var key = Fp.MethodKey(m);
                var mh = Fp.MethodHash(m);
                string sh;
                bool inStock = st.Methods.TryGetValue(key, out sh);
                if (inStock && sh == mh) continue; // the mod did not touch it
                MethodDefinition tm;
                if (!tMethods.TryGetValue(key, out tm))
                {
                    addMethods.Add(m); rep.MethodsAdded++;
                    continue;
                }
                var th = Fp.MethodHash(tm);
                if (th == mh) { rep.MethodsSame++; continue; }
                replaceBodies.Add(new KeyValuePair<MethodDefinition, MethodDefinition>(m, tm));
                if (inStock && th == sh) rep.MethodsReplaced++;
                else
                {
                    rep.MethodsReplaced++;
                    rep.Conflicts.Add("Method " + mt.FullName + "." + m.Name + " was also changed by another mod.");
                }
            }

            // properties / events whose accessors are new
            var tProps = new HashSet<string>(tt.Properties.Select(p => p.Name));
            foreach (var p in mt.Properties) if (!tProps.Contains(p.Name)) addProps.Add(p);
            var tEvents = new HashSet<string>(tt.Events.Select(e => e.Name));
            foreach (var e in mt.Events) if (!tEvents.Contains(e.Name)) addEvents.Add(e);

            // nested types
            foreach (var n in mt.NestedTypes) PlanType(n, false);
        }

        // ---------------------------------------------------------------- applying
        public MergeReport Apply()
        {
            Plan();

            // 0. classes that clash: drop the target's copy, ours replaces it
            foreach (var mt in replaceTypes)
            {
                var tt = tTypes[mt.FullName];
                if (tt.DeclaringType != null) tt.DeclaringType.NestedTypes.Remove(tt);
                else target.Types.Remove(tt);
                foreach (var t in Walk(tt)) tTypes.Remove(t.FullName);
                addTypes.Add(mt);
            }

            // 1. shells of every new type (recursively), so references can resolve
            var newTypes = new List<KeyValuePair<TypeDefinition, TypeDefinition>>(); // mod, target
            foreach (var mt in addTypes)
            {
                TypeDefinition parent = null;
                if (mt.DeclaringType != null) parent = tTypes[mt.DeclaringType.FullName];
                CreateShell(mt, parent, newTypes);
            }

            // 2. type headers, generic params, fields, method shells, for new types
            foreach (var kv in newTypes) FillTypeHeader(kv.Key, kv.Value);
            var bodyJobs = new List<KeyValuePair<MethodDefinition, MethodDefinition>>();
            var memberJobs = new List<KeyValuePair<TypeDefinition, TypeDefinition>>();
            foreach (var kv in newTypes)
            {
                foreach (var f in kv.Key.Fields) kv.Value.Fields.Add(CloneField(f));
                foreach (var m in kv.Key.Methods)
                {
                    var nm = CloneMethodShell(m);
                    kv.Value.Methods.Add(nm);
                    bodyJobs.Add(new KeyValuePair<MethodDefinition, MethodDefinition>(m, nm));
                }
                memberJobs.Add(kv);
            }
            // added members of existing game types
            foreach (var f in addFields) tTypes[f.DeclaringType.FullName].Fields.Add(CloneField(f));
            foreach (var m in addMethods)
            {
                var nm = CloneMethodShell(m);
                tTypes[m.DeclaringType.FullName].Methods.Add(nm);
                bodyJobs.Add(new KeyValuePair<MethodDefinition, MethodDefinition>(m, nm));
            }
            foreach (var kv in headerChanges)
            {
                kv.Value.Attributes = kv.Key.Attributes;
                if (kv.Key.BaseType != null) kv.Value.BaseType = ImportType(kv.Key.BaseType);
                var have = new HashSet<string>(kv.Value.Interfaces.Select(i => i.InterfaceType.FullName));
                foreach (var i in kv.Key.Interfaces)
                    if (!have.Contains(i.InterfaceType.FullName)) kv.Value.Interfaces.Add(new InterfaceImplementation(ImportType(i.InterfaceType)));
            }

            // 3. properties, events, attributes, bodies
            foreach (var kv in memberJobs)
            {
                foreach (var p in kv.Key.Properties) kv.Value.Properties.Add(CloneProperty(p, kv.Value));
                foreach (var e in kv.Key.Events) kv.Value.Events.Add(CloneEvent(e, kv.Value));
                CopyAttributes(kv.Key, kv.Value);
                for (int i = 0; i < kv.Key.Fields.Count; i++) CopyAttributes(kv.Key.Fields[i], kv.Value.Fields[i]);
                for (int i = 0; i < kv.Key.GenericParameters.Count; i++) CopyConstraints(kv.Key.GenericParameters[i], kv.Value.GenericParameters[i]);
            }
            foreach (var f in addFields) CopyAttributes(f, FindField(tTypes[f.DeclaringType.FullName], f.Name));
            foreach (var p in addProps)
            {
                var tt = tTypes[p.DeclaringType.FullName];
                tt.Properties.Add(CloneProperty(p, tt));
            }
            foreach (var e in addEvents)
            {
                var tt = tTypes[e.DeclaringType.FullName];
                tt.Events.Add(CloneEvent(e, tt));
            }
            foreach (var kv in bodyJobs)
            {
                CopyMethodExtras(kv.Key, kv.Value);
                CloneBody(kv.Key, kv.Value);
            }
            foreach (var kv in replaceBodies)
            {
                kv.Value.Attributes = kv.Key.Attributes;
                kv.Value.ImplAttributes = kv.Key.ImplAttributes;
                CloneBody(kv.Key, kv.Value);
            }
            return rep;
        }

        static IEnumerable<TypeDefinition> Walk(TypeDefinition t)
        {
            yield return t;
            foreach (var n in t.NestedTypes) foreach (var x in Walk(n)) yield return x;
        }

        void CreateShell(TypeDefinition mt, TypeDefinition parent, List<KeyValuePair<TypeDefinition, TypeDefinition>> list)
        {
            var nt = new TypeDefinition(mt.Namespace, mt.Name, mt.Attributes);
            nt.PackingSize = mt.PackingSize;
            nt.ClassSize = mt.ClassSize;
            foreach (var gp in mt.GenericParameters)
                nt.GenericParameters.Add(new GenericParameter(gp.Name, nt) { Attributes = gp.Attributes });
            if (parent != null) parent.NestedTypes.Add(nt); else target.Types.Add(nt);
            tTypes[mt.FullName] = nt;
            list.Add(new KeyValuePair<TypeDefinition, TypeDefinition>(mt, nt));
            foreach (var n in mt.NestedTypes) CreateShell(n, nt, list);
        }

        void FillTypeHeader(TypeDefinition mt, TypeDefinition nt)
        {
            if (mt.BaseType != null) nt.BaseType = ImportType(mt.BaseType);
            foreach (var i in mt.Interfaces)
            {
                var ii = new InterfaceImplementation(ImportType(i.InterfaceType));
                CopyAttributes(i, ii);
                nt.Interfaces.Add(ii);
            }
        }

        FieldDefinition CloneField(FieldDefinition f)
        {
            var nf = new FieldDefinition(f.Name, f.Attributes, ImportType(f.FieldType));
            if (f.HasConstant) nf.Constant = f.Constant;
            if (f.InitialValue != null && f.InitialValue.Length > 0) nf.InitialValue = (byte[])f.InitialValue.Clone();
            if (f.HasLayoutInfo) nf.Offset = f.Offset;
            if (f.HasMarshalInfo) nf.MarshalInfo = f.MarshalInfo;
            return nf;
        }

        MethodDefinition CloneMethodShell(MethodDefinition m)
        {
            var nm = new MethodDefinition(m.Name, m.Attributes, target.TypeSystem.Void);
            nm.ImplAttributes = m.ImplAttributes;
            nm.SemanticsAttributes = m.SemanticsAttributes;
            nm.HasThis = m.HasThis;
            nm.ExplicitThis = m.ExplicitThis;
            nm.CallingConvention = m.CallingConvention;
            foreach (var gp in m.GenericParameters)
                nm.GenericParameters.Add(new GenericParameter(gp.Name, nm) { Attributes = gp.Attributes });
            nm.ReturnType = ImportType(m.ReturnType);
            foreach (var p in m.Parameters)
            {
                var np = new ParameterDefinition(p.Name, p.Attributes, ImportType(p.ParameterType));
                if (p.HasConstant) np.Constant = p.Constant;
                if (p.HasMarshalInfo) np.MarshalInfo = p.MarshalInfo;
                nm.Parameters.Add(np);
            }
            if (m.HasPInvokeInfo)
            {
                var mref = target.ModuleReferences.FirstOrDefault(r => r.Name == m.PInvokeInfo.Module.Name);
                if (mref == null) { mref = new ModuleReference(m.PInvokeInfo.Module.Name); target.ModuleReferences.Add(mref); }
                nm.PInvokeInfo = new PInvokeInfo(m.PInvokeInfo.Attributes, m.PInvokeInfo.EntryPoint, mref);
            }
            return nm;
        }

        void CopyMethodExtras(MethodDefinition m, MethodDefinition nm)
        {
            CopyAttributes(m, nm);
            CopyAttributes(m.MethodReturnType, nm.MethodReturnType);
            for (int i = 0; i < m.Parameters.Count; i++) CopyAttributes(m.Parameters[i], nm.Parameters[i]);
            for (int i = 0; i < m.GenericParameters.Count; i++) CopyConstraints(m.GenericParameters[i], nm.GenericParameters[i]);
            foreach (var o in m.Overrides) nm.Overrides.Add(ImportMethod(o));
        }

        void CopyConstraints(GenericParameter from, GenericParameter to)
        {
            foreach (var c in from.Constraints)
                to.Constraints.Add(new GenericParameterConstraint(ImportType(c.ConstraintType)));
            CopyAttributes(from, to);
        }

        PropertyDefinition CloneProperty(PropertyDefinition p, TypeDefinition owner)
        {
            var np = new PropertyDefinition(p.Name, p.Attributes, ImportType(p.PropertyType));
            np.HasThis = p.HasThis;
            foreach (var pp in p.Parameters) np.Parameters.Add(new ParameterDefinition(pp.Name, pp.Attributes, ImportType(pp.ParameterType)));
            if (p.GetMethod != null) np.GetMethod = FindMethod(owner, p.GetMethod);
            if (p.SetMethod != null) np.SetMethod = FindMethod(owner, p.SetMethod);
            foreach (var om in p.OtherMethods) np.OtherMethods.Add(FindMethod(owner, om));
            if (p.HasConstant) np.Constant = p.Constant;
            CopyAttributes(p, np);
            return np;
        }

        EventDefinition CloneEvent(EventDefinition e, TypeDefinition owner)
        {
            var ne = new EventDefinition(e.Name, e.Attributes, ImportType(e.EventType));
            if (e.AddMethod != null) ne.AddMethod = FindMethod(owner, e.AddMethod);
            if (e.RemoveMethod != null) ne.RemoveMethod = FindMethod(owner, e.RemoveMethod);
            if (e.InvokeMethod != null) ne.InvokeMethod = FindMethod(owner, e.InvokeMethod);
            foreach (var om in e.OtherMethods) ne.OtherMethods.Add(FindMethod(owner, om));
            CopyAttributes(e, ne);
            return ne;
        }

        static MethodDefinition FindMethod(TypeDefinition owner, MethodDefinition like)
        {
            var key = Fp.MethodKey(like);
            foreach (var m in owner.Methods) if (Fp.MethodKey(m) == key) return m;
            throw new InvalidOperationException("Method not found after copy: " + owner.FullName + "::" + key);
        }

        static FieldDefinition FindField(TypeDefinition owner, string name)
        {
            foreach (var f in owner.Fields) if (f.Name == name) return f;
            throw new InvalidOperationException("Field not found after copy: " + owner.FullName + "::" + name);
        }

        // ---------------------------------------------------------------- bodies
        void CloneBody(MethodDefinition m, MethodDefinition nm)
        {
            if (!m.HasBody) { nm.Body = null; return; }
            var b = m.Body;
            var nb = new MethodBody(nm);
            nm.Body = nb;
            nb.InitLocals = b.InitLocals;
            nb.MaxStackSize = b.MaxStackSize;
            foreach (var v in b.Variables) nb.Variables.Add(new VariableDefinition(ImportType(v.VariableType)));

            var map = new Dictionary<Instruction, Instruction>();
            foreach (var i in b.Instructions)
            {
                var ni = Instruction.Create(OpCodes.Nop);
                ni.OpCode = i.OpCode;
                map[i] = ni;
                nb.Instructions.Add(ni);
            }
            foreach (var i in b.Instructions)
            {
                var ni = map[i];
                var op = i.Operand;
                if (op == null) continue;
                var ins = op as Instruction;
                if (ins != null) { ni.Operand = map[ins]; continue; }
                var arr = op as Instruction[];
                if (arr != null) { ni.Operand = arr.Select(a => map[a]).ToArray(); continue; }
                var v = op as VariableDefinition;
                if (v != null) { ni.Operand = nb.Variables[v.Index]; continue; }
                var p = op as ParameterDefinition;
                if (p != null)
                {
                    ni.Operand = (p.Index < 0 || p == b.ThisParameter) ? nb.ThisParameter : nm.Parameters[p.Index];
                    continue;
                }
                var mr = op as MethodReference;
                if (mr != null) { ni.Operand = ImportMethod(mr); continue; }
                var fr = op as FieldReference;
                if (fr != null) { ni.Operand = ImportField(fr); continue; }
                var tr = op as TypeReference;
                if (tr != null) { ni.Operand = ImportType(tr); continue; }
                var cs = op as CallSite;
                if (cs != null)
                {
                    var ncs = new CallSite(ImportType(cs.ReturnType)) { HasThis = cs.HasThis, ExplicitThis = cs.ExplicitThis, CallingConvention = cs.CallingConvention };
                    foreach (var cp in cs.Parameters) ncs.Parameters.Add(new ParameterDefinition(cp.Name, cp.Attributes, ImportType(cp.ParameterType)));
                    ni.Operand = ncs;
                    continue;
                }
                ni.Operand = op; // string, numbers
            }
            foreach (var h in b.ExceptionHandlers)
            {
                var nh = new ExceptionHandler(h.HandlerType);
                nh.TryStart = Map(map, h.TryStart);
                nh.TryEnd = Map(map, h.TryEnd);
                nh.HandlerStart = Map(map, h.HandlerStart);
                nh.HandlerEnd = Map(map, h.HandlerEnd);
                nh.FilterStart = Map(map, h.FilterStart);
                if (h.CatchType != null) nh.CatchType = ImportType(h.CatchType);
                nb.ExceptionHandlers.Add(nh);
            }
        }

        static Instruction Map(Dictionary<Instruction, Instruction> map, Instruction i)
        {
            return i == null ? null : map[i];
        }

        // ---------------------------------------------------------------- references
        bool IsModLocal(TypeReference t)
        {
            while (t.DeclaringType != null) t = t.DeclaringType;
            if (t is TypeDefinition) return ((TypeDefinition)t).Module == mod;
            var scope = t.Scope;
            if (scope == null) return false;
            if (scope.MetadataScopeType == MetadataScopeType.ModuleDefinition) return true;
            // a reference to the mod assembly itself by name
            var an = scope as AssemblyNameReference;
            return an != null && an.Name == mod.Assembly.Name.Name;
        }

        public TypeReference ImportType(TypeReference t)
        {
            if (t == null) return null;
            var gp = t as GenericParameter;
            if (gp != null) return MakeGp(gp.Position, gp.Type);
            var git = t as GenericInstanceType;
            if (git != null)
            {
                var n = new GenericInstanceType(ImportType(git.ElementType));
                foreach (var a in git.GenericArguments) n.GenericArguments.Add(ImportType(a));
                return n;
            }
            var at = t as ArrayType;
            if (at != null)
            {
                var n = new ArrayType(ImportType(at.ElementType));
                if (!at.IsVector)
                {
                    n.Dimensions.Clear();
                    foreach (var d in at.Dimensions) n.Dimensions.Add(new ArrayDimension(d.LowerBound, d.UpperBound));
                }
                return n;
            }
            if (t is ByReferenceType) return new ByReferenceType(ImportType(((ByReferenceType)t).ElementType));
            if (t is PointerType) return new PointerType(ImportType(((PointerType)t).ElementType));
            if (t is PinnedType) return new PinnedType(ImportType(((PinnedType)t).ElementType));
            if (t is SentinelType) return new SentinelType(ImportType(((SentinelType)t).ElementType));
            var rm = t as RequiredModifierType;
            if (rm != null) return new RequiredModifierType(ImportType(rm.ModifierType), ImportType(rm.ElementType));
            var om = t as OptionalModifierType;
            if (om != null) return new OptionalModifierType(ImportType(om.ModifierType), ImportType(om.ElementType));
            if (t is TypeSpecification) throw new NotSupportedException("Type form not supported: " + t.GetType().Name + " " + t.FullName);

            if (IsModLocal(t))
            {
                TypeDefinition td;
                if (tTypes.TryGetValue(t.FullName, out td)) return td;
                throw new InvalidOperationException("Class missing in target: " + t.FullName);
            }
            if (t.IsPrimitive || t.FullName == "System.Object" || t.FullName == "System.String" || t.FullName == "System.Void" || t.FullName == "System.TypedReference")
            {
                var ts = TypeSystemType(t.FullName);
                if (ts != null) return ts;
            }
            return target.ImportReference(t);
        }

        // An owner-less generic parameter (!0 / !!0). Cecil only writes kind + position for it.
        static System.Reflection.ConstructorInfo gpCtor;
        GenericParameter MakeGp(int position, GenericParameterType kind)
        {
            if (gpCtor == null)
                gpCtor = typeof(GenericParameter).GetConstructor(
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance,
                    null, new[] { typeof(int), typeof(GenericParameterType), typeof(ModuleDefinition) }, null);
            return (GenericParameter)gpCtor.Invoke(new object[] { position, kind, target });
        }

        TypeReference TypeSystemType(string fullName)
        {
            var ts = target.TypeSystem;
            switch (fullName)
            {
                case "System.Void": return ts.Void;
                case "System.Boolean": return ts.Boolean;
                case "System.Char": return ts.Char;
                case "System.SByte": return ts.SByte;
                case "System.Byte": return ts.Byte;
                case "System.Int16": return ts.Int16;
                case "System.UInt16": return ts.UInt16;
                case "System.Int32": return ts.Int32;
                case "System.UInt32": return ts.UInt32;
                case "System.Int64": return ts.Int64;
                case "System.UInt64": return ts.UInt64;
                case "System.Single": return ts.Single;
                case "System.Double": return ts.Double;
                case "System.IntPtr": return ts.IntPtr;
                case "System.UIntPtr": return ts.UIntPtr;
                case "System.String": return ts.String;
                case "System.Object": return ts.Object;
                case "System.TypedReference": return ts.TypedReference;
            }
            return null;
        }

        public MethodReference ImportMethod(MethodReference mr)
        {
            var gim = mr as GenericInstanceMethod;
            if (gim != null)
            {
                var n = new GenericInstanceMethod(ImportMethod(gim.ElementMethod));
                foreach (var a in gim.GenericArguments) n.GenericArguments.Add(ImportType(a));
                return n;
            }
            var decl = ImportType(mr.DeclaringType);
            var td = decl as TypeDefinition;
            if (td != null && td.Module == target)
            {
                var key = Fp.MethodKey(mr.Resolve() ?? (mr as MethodDefinition) ?? throw new InvalidOperationException("Cannot resolve " + mr.FullName));
                foreach (var m in td.Methods) if (Fp.MethodKey(m) == key) return m;
                throw new InvalidOperationException("Method missing in target: " + mr.FullName);
            }
            var nr = new MethodReference(mr.Name, target.TypeSystem.Void, decl)
            {
                HasThis = mr.HasThis,
                ExplicitThis = mr.ExplicitThis,
                CallingConvention = mr.CallingConvention
            };
            foreach (var gp in mr.GenericParameters) nr.GenericParameters.Add(new GenericParameter(gp.Name, nr));
            nr.ReturnType = ImportType(mr.ReturnType);
            foreach (var p in mr.Parameters) nr.Parameters.Add(new ParameterDefinition(p.Name, p.Attributes, ImportType(p.ParameterType)));
            return nr;
        }

        public FieldReference ImportField(FieldReference fr)
        {
            var decl = ImportType(fr.DeclaringType);
            var td = decl as TypeDefinition;
            if (td != null && td.Module == target)
            {
                foreach (var f in td.Fields) if (f.Name == fr.Name) return f;
                throw new InvalidOperationException("Field missing in target: " + fr.FullName);
            }
            return new FieldReference(fr.Name, ImportType(fr.FieldType), decl);
        }

        // ---------------------------------------------------------------- attributes
        void CopyAttributes(ICustomAttributeProvider from, ICustomAttributeProvider to)
        {
            if (!from.HasCustomAttributes) return;
            foreach (var ca in from.CustomAttributes)
            {
                var n = new CustomAttribute(ImportMethod(ca.Constructor));
                foreach (var a in ca.ConstructorArguments) n.ConstructorArguments.Add(ImportArg(a));
                foreach (var f in ca.Fields) n.Fields.Add(new CustomAttributeNamedArgument(f.Name, ImportArg(f.Argument)));
                foreach (var p in ca.Properties) n.Properties.Add(new CustomAttributeNamedArgument(p.Name, ImportArg(p.Argument)));
                to.CustomAttributes.Add(n);
            }
        }

        CustomAttributeArgument ImportArg(CustomAttributeArgument a)
        {
            object v = a.Value;
            if (v is TypeReference) v = ImportType((TypeReference)v);
            else if (v is CustomAttributeArgument) v = ImportArg((CustomAttributeArgument)v);
            else if (v is CustomAttributeArgument[]) v = ((CustomAttributeArgument[])v).Select(ImportArg).ToArray();
            return new CustomAttributeArgument(ImportType(a.Type), v);
        }
    }
}
