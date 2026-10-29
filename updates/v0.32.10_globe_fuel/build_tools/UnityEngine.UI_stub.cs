[assembly: System.Reflection.AssemblyVersion("1.0.0.0")]
namespace UnityEngine.UI {
public class UIBehaviour : UnityEngine.MonoBehaviour {}
public class Graphic : UIBehaviour { public virtual UnityEngine.Color color { get; set; } public virtual UnityEngine.Material material { get; set; } public UnityEngine.RectTransform rectTransform { get { return null; } } public virtual bool raycastTarget { get; set; } public UnityEngine.Canvas canvas { get { return null; } } }
public class MaskableGraphic : Graphic {}
public class Text : MaskableGraphic { public virtual string text { get; set; } public UnityEngine.FontStyle fontStyle { get; set; } public UnityEngine.HorizontalWrapMode horizontalOverflow { get; set; } public UnityEngine.VerticalWrapMode verticalOverflow { get; set; } public UnityEngine.Font font { get; set; } public int fontSize { get; set; } public bool supportRichText { get; set; } public UnityEngine.TextAnchor alignment { get; set; } public float preferredWidth { get { return 0; } } public float preferredHeight { get { return 0; } } }
public class Image : MaskableGraphic { public UnityEngine.Sprite sprite { get; set; } public bool preserveAspect { get; set; } public float fillAmount { get; set; } }
public class Selectable : UIBehaviour { public bool interactable { get; set; } }
public class Button : Selectable {}
public class Toggle : Selectable { public bool isOn { get; set; } }
public class Slider : Selectable { public float value { get; set; } }
public class Dropdown : Selectable { public int value { get; set; } }
public class InputField : Selectable { public string text { get; set; } }
public class ScrollRect : UIBehaviour {}
public class Outline : UIBehaviour {}
public class Shadow : UIBehaviour {}
public class CanvasScaler : UIBehaviour { public float scaleFactor { get; set; } }
public class LayoutElement : UIBehaviour {}
public class GridLayoutGroup : UIBehaviour {}
public class HorizontalLayoutGroup : UIBehaviour {}
public class VerticalLayoutGroup : UIBehaviour {}
public class ContentSizeFitter : UIBehaviour {}
public class RawImage : MaskableGraphic {}
public class Scrollbar : Selectable {}
public class Mask : UIBehaviour {}
}

namespace UnityEngine.EventSystems {
public abstract class UIBehaviour : UnityEngine.MonoBehaviour {}
public abstract class AbstractEventData { }
public class BaseEventData : AbstractEventData { public BaseEventData(EventSystem eventSystem) {} }
public class PointerEventData : BaseEventData { public PointerEventData(EventSystem eventSystem) : base(eventSystem) {} public UnityEngine.Vector2 position { get; set; } }
public struct RaycastResult { public UnityEngine.GameObject gameObject { get { return null; } set {} } }
public class EventSystem : UIBehaviour { public static EventSystem current { get { return null; } set {} } public void RaycastAll(PointerEventData eventData, System.Collections.Generic.List<RaycastResult> raycastResults) {} public bool IsPointerOverGameObject() { return false; } }
}
