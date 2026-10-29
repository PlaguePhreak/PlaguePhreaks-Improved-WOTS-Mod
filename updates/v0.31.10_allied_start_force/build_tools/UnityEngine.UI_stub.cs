[assembly: System.Reflection.AssemblyVersion("1.0.0.0")]
namespace UnityEngine.UI {
public class UIBehaviour : UnityEngine.MonoBehaviour {}
public class Graphic : UIBehaviour { public virtual UnityEngine.Color color { get; set; } public UnityEngine.RectTransform rectTransform { get { return null; } } public virtual bool raycastTarget { get; set; } }
public class MaskableGraphic : Graphic {}
public class Text : MaskableGraphic { public float lineSpacing { get; set; } public virtual string text { get; set; } public UnityEngine.Font font { get; set; } public int fontSize { get; set; } public bool supportRichText { get; set; } public UnityEngine.TextAnchor alignment { get; set; } public float preferredWidth { get { return 0; } } public float preferredHeight { get { return 0; } } public UnityEngine.HorizontalWrapMode horizontalOverflow { get; set; } public UnityEngine.VerticalWrapMode verticalOverflow { get; set; } }
public class Image : MaskableGraphic { public UnityEngine.Sprite sprite { get; set; } public float fillAmount { get; set; } }
public class Selectable : UIBehaviour { public bool interactable { get; set; } public Graphic targetGraphic { get; set; } }
public class Button : Selectable { public class ButtonClickedEvent : UnityEngine.Events.UnityEvent {} public ButtonClickedEvent onClick { get; set; } }
public class Toggle : Selectable { public bool isOn { get; set; } }
public class Slider : Selectable { public float value { get; set; } }
public class Dropdown : Selectable { public int value { get; set; } }
public class InputField : Selectable { public string text { get; set; } }
public class ScrollRect : UIBehaviour { public enum MovementType { Unrestricted, Elastic, Clamped } public enum ScrollbarVisibility { Permanent, AutoHide, AutoHideAndExpandViewport } public UnityEngine.RectTransform content { get; set; } public UnityEngine.RectTransform viewport { get; set; } public bool horizontal { get; set; } public bool vertical { get; set; } public MovementType movementType { get; set; } public float scrollSensitivity { get; set; } public Scrollbar verticalScrollbar { get; set; } public ScrollbarVisibility verticalScrollbarVisibility { get; set; } }
public class Outline : UIBehaviour {}
public class Shadow : UIBehaviour {}
public class CanvasScaler : UIBehaviour { public float scaleFactor { get; set; } }
public class LayoutElement : UIBehaviour {}

public abstract class LayoutGroup : UIBehaviour {}
public abstract class HorizontalOrVerticalLayoutGroup : LayoutGroup {}
public class HorizontalLayoutGroup : HorizontalOrVerticalLayoutGroup {}
public class VerticalLayoutGroup : HorizontalOrVerticalLayoutGroup {}
public class GridLayoutGroup : LayoutGroup {}
public class RectMask2D : UIBehaviour {}
public class GraphicRaycaster : UIBehaviour {}
public class ContentSizeFitter : UIBehaviour { public enum FitMode { Unconstrained, MinSize, PreferredSize } public FitMode horizontalFit { get; set; } public FitMode verticalFit { get; set; } }
public class RawImage : MaskableGraphic {}
public class Scrollbar : Selectable { public enum Direction { LeftToRight, RightToLeft, BottomToTop, TopToBottom } public UnityEngine.RectTransform handleRect { get; set; } public Direction direction { get; set; } }
public class Mask : UIBehaviour {}
}
