// WOTS mod installer - shared core. Builds stable, module-independent fingerprints of
// types and method bodies so three copies of Assembly-CSharp.dll can be compared.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace WotsInstaller
{
    public static class Fp
    {
        public static IEnumerable<TypeDefinition> AllTypes(ModuleDefinition m)
        {
            foreach (var t in m.Types)
                foreach (var x in Walk(t)) yield return x;
        }
        static IEnumerable<TypeDefinition> Walk(TypeDefinition t)
        {
            yield return t;
            foreach (var n in t.NestedTypes)
                foreach (var x in Walk(n)) yield return x;
        }

        public static string MethodKey(MethodDefinition m)
        {
            // name + generic arity + parameter types + return type; declaring type is the container.
            var sb = new StringBuilder();
            sb.Append(m.ReturnType.FullName).Append(' ').Append(m.Name);
            if (m.HasGenericParameters) sb.Append('`').Append(m.GenericParameters.Count);
            sb.Append('(');
            for (int i = 0; i < m.Parameters.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(m.Parameters[i].ParameterType.FullName);
            }
            sb.Append(')');
            return sb.ToString();
        }

        static string Op(object o, MethodBody body)
        {
            if (o == null) return "";
            var ins = o as Instruction;
            if (ins != null) return "@" + body.Instructions.IndexOf(ins);
            var arr = o as Instruction[];
            if (arr != null)
            {
                var sb = new StringBuilder("[");
                foreach (var a in arr) sb.Append(body.Instructions.IndexOf(a)).Append(',');
                return sb.Append(']').ToString();
            }
            var v = o as VariableDefinition;
            if (v != null) return "V" + v.Index;
            var p = o as ParameterDefinition;
            if (p != null) return "P" + p.Sequence;
            var mr = o as MemberReference;
            if (mr != null) return mr.FullName;
            var s = o as string;
            if (s != null) return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
            var cs = o as CallSite;
            if (cs != null) return cs.FullName;
            return Num(o);
        }

        // Runtime-independent text for constants (float "R" formatting differs between
        // .NET Framework / Mono and .NET Core, so floats are written as their bits).
        public static string Num(object o)
        {
            if (o == null) return "null";
            if (o is float) return "f" + BitConverter.ToInt32(BitConverter.GetBytes((float)o), 0).ToString("x8");
            if (o is double) return "d" + BitConverter.DoubleToInt64Bits((double)o).ToString("x16");
            return Convert.ToString(o, CultureInfo.InvariantCulture);
        }

        public static string BodyText(MethodDefinition m)
        {
            var sb = new StringBuilder();
            sb.Append((int)m.Attributes).Append('/').Append((int)m.ImplAttributes).Append('\n');
            if (!m.HasBody) return sb.Append("nobody").ToString();
            var b = m.Body;
            sb.Append("init=").Append(b.InitLocals).Append('\n');
            foreach (var v in b.Variables) sb.Append("L ").Append(v.VariableType.FullName).Append('\n');
            foreach (var i in b.Instructions)
                sb.Append(i.OpCode.Name).Append(' ').Append(Op(i.Operand, b)).Append('\n');
            foreach (var h in b.ExceptionHandlers)
            {
                sb.Append("EH ").Append(h.HandlerType).Append(' ')
                  .Append(Op(h.TryStart, b)).Append(Op(h.TryEnd, b)).Append(Op(h.HandlerStart, b))
                  .Append(Op(h.HandlerEnd, b)).Append(Op(h.FilterStart, b)).Append(' ')
                  .Append(h.CatchType == null ? "" : h.CatchType.FullName).Append('\n');
            }
            return sb.ToString();
        }

        public static string Hash(string s)
        {
            using (var sha = SHA1.Create())
            {
                var h = sha.ComputeHash(Encoding.UTF8.GetBytes(s));
                var sb = new StringBuilder();
                for (int i = 0; i < 10; i++) sb.Append(h[i].ToString("x2"));
                return sb.ToString();
            }
        }

        public static string MethodHash(MethodDefinition m) { return Hash(BodyText(m)); }

        public static string FieldText(FieldDefinition f)
        {
            return f.FieldType.FullName + "/" + (int)f.Attributes + "/" + (f.HasConstant ? Num(f.Constant) : "");
        }

        public static string TypeHeader(TypeDefinition t)
        {
            var sb = new StringBuilder();
            sb.Append((int)t.Attributes).Append(' ').Append(t.BaseType == null ? "" : t.BaseType.FullName);
            foreach (var i in t.Interfaces) sb.Append(" I:").Append(i.InterfaceType.FullName);
            return sb.ToString();
        }

        // Whole-type fingerprint (used to test "is this added type already identical").
        public static string TypeHash(TypeDefinition t)
        {
            var sb = new StringBuilder(TypeHeader(t)).Append('\n');
            foreach (var f in t.Fields) sb.Append("F ").Append(f.Name).Append(' ').Append(FieldText(f)).Append('\n');
            foreach (var m in t.Methods) sb.Append("M ").Append(MethodKey(m)).Append(' ').Append(MethodHash(m)).Append('\n');
            foreach (var n in t.NestedTypes) sb.Append("N ").Append(TypeHash(n)).Append('\n');
            return Hash(sb.ToString());
        }
    }
}
