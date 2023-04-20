from typing import Union, Literal, Optional
import random
from htmltools import tags, div, css, TagChild, TagAttrs, Tag, HTMLDependency
import numbers


class Sidebar:
    def __init__(self, tag, collapse_tag, position, open, width, max_height_mobile):
        self.tag = tag
        self.collapse_tag = collapse_tag
        self.position = position
        self.open = open
        self.width = width
        self.max_height_mobile = max_height_mobile


def sidebar(
    *args: Union[TagChild, TagAttrs],
    width: int = 250,
    position="left",
    open: Union[
        Literal["desktop"], Literal["open"], Literal["closed"], Literal["always"]
    ] = "desktop",
    id: Optional[str] = None,
    title: Union[TagChild, str, numbers.Number] = None,
    bg=None,
    fg=None,
    class_=None,
    max_height_mobile=None,
):
    # TODO: validate `open`, bg, fg, class_, max_height_mobile
    # TODO: Add type annotations

    if id is not None:
        class_ = "bslib-sidebar-input" + ("" if not class_ else (" " + class_))
    elif open != "always":
        # but always provide id when collapsible for accessibility reasons
        id = f"bslib-sidebar-{random.randint(1000, 10000)}"

    if fg is None and bg is not None:
        fg = get_color_contrast(bg)
    if bg is None and fg is not None:
        bg = get_color_contrast(fg)

    if isinstance(title, str) or isinstance(title, numbers.Number):
        title = div(title, class_="sidebar-title")

    collapse_tag = None
    if open != "always":
        collapse_tag = tags.button(
            collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            style=css(background_color=bg, color=fg),
            aria_expanded="true" if open in ["open", "desktop"] else "false",
            aria_controls=id,
        )

    tag = div(
        div(title, *args, class_="sidebar-content"),
        {"class": "sidebar"},
        id=id,
        role="complementary",
        class_=class_,
        style=css(background_color=bg, color=fg),
    )

    return Sidebar(
        tag=tag,
        collapse_tag=collapse_tag,
        position=position,
        open=open,
        width=width,
        max_height_mobile=max_height_mobile,
    )


def get_color_contrast(color: str) -> str:
    # TODO: Implement
    return None


def collapse_icon() -> Tag:
    return tags.svg(
        dict(
            xmlns="http://www.w3.org/2000/svg",
            viewBox="0 0 16 16",
            class_="bi bi-chevron-down collapse-icon",
            style="fill:currentColor;",
            aria_hidden="true",
            role="img",
        ),
        Tag(
            "path",
            dict(
                fill_rule="evenodd",
                d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z",
            ),
        ),
    )


def layout_sidebar(
    sidebar: Sidebar,
    *args,
    fillable=False,
    fill=True,
    bg=None,
    fg=None,
    border: Union[None, bool] = None,
    border_radius=None,
    border_color=None,
    height=None,
):
    # TODO: validate sidebar object, border, border_radius, colors

    if fg is None and bg is not None:
        fg = get_color_contrast(bg)
    if bg is None and fg is not None:
        bg = get_color_contrast(fg)

    main = div(
        *args,
        role="main",
        class_="main",
        style=css(background_color=bg, color=fg),
    )

    main = bind_fill_role(main, container=fillable)

    contents = [main, sidebar.tag, sidebar.collapse_tag]

    right = sidebar.position == "right"

    max_height_mobile = sidebar.max_height_mobile or (
        "250px" if height is None else "50%"
    )

    res = div(
        sidebar_dependency(),
        sidebar_js_init(),
        dict(class_="bslib-sidebar-layout"),
        dict(class_="sidebar-right") if right else None,
        dict(class_="sidebar-collapsed") if sidebar.open == "closed" else None,
        *contents,
        data_sidebar_init_auto_collapse="true" if sidebar.open == "desktop" else None,
        data_bslib_sidebar_border=trinary(border),
        data_bslib_sidebar_border_radius=trinary(border_radius),
        style=css(
            __bslib_sidebar_width=sidebar.width,
            __bs_card_border_color=border_color,
            # TODO: validateCssUnit(height)
            height=height,
            __bslib_sidebar_max_height_mobile=max_height_mobile,
        ),
    )

    res = bind_fill_role(res, item=fill)

    # res <- as.card_item(res)
    # as_fragment(
    #     tag_require(res, version = 5, caller = "layout_sidebar()")
    # )
    return res


def trinary(x: Optional[bool]) -> Union[None, str]:
    if x is None:
        return None
    if x:
        return "true"
    else:
        return "false"


def bind_fill_role(
    tag: Tag, *, item: Optional[bool] = None, container: Optional[bool] = None
) -> Tag:
    if item is not None:
        if item:
            tag.add_class("html-fill-item")
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-item")
            ...

    if container is not None:
        if container:
            tag.add_class("html-fill-container")
            tag.append(fill_dependencies())
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-container")
            ...

    return tag


def sidebar_js_init():
    return tags.script(
        dict(data_bslib_sidebar_init=True),
        """
        var thisScript = document.querySelector('script[data-bslib-sidebar-init]');
        thisScript.removeAttribute('data-bslib-sidebar-init');

        // If this layout is the innermost layout, then allow it to add CSS
        // variables to it and its ancestors (counting how parent layouts there are)
        var thisLayout = $(thisScript).parent();
        var noChildLayouts = thisLayout.find('.bslib-sidebar-layout').length === 0;
        if (noChildLayouts) {
        var parentLayouts = thisLayout.parents('.bslib-sidebar-layout');
        // .add() sorts the layouts in DOM order (i.e., innermost is last)
        var layouts = thisLayout.add(parentLayouts);
        var ctrs = {left: 0, right: 0};
        layouts.each(function(i, x) {
            $(x).css('--bslib-sidebar-counter', i);
            var right = $(x).hasClass('sidebar-right');
            $(x).css('--bslib-sidebar-overlap-counter', right ? ctrs.right : ctrs.left);
            right ? ctrs.right++ : ctrs.left++;
        });
        }

        // If sidebar is marked open='desktop', collapse sidebar if on mobile
        if (thisLayout.data('sidebarInitAutoCollapse')) {
        var initCollapsed = thisLayout.css('--bslib-sidebar-js-init-collapsed');
        if (initCollapsed === 'true') {
            thisLayout.addClass('sidebar-collapsed');
            thisLayout.find('.collapse-toggle').attr('aria-expanded', 'false');
        }
        }
        """,
    )


def sidebar_dependency():
    return HTMLDependency(
        "bslib-sidebar",
        "0.0.0",
        source={
            "package": "bslib",
            "subdir": "sidebar/",
        },
        script={"src": "sidebar.min.js"},
    )


def fill_dependencies():
    return HTMLDependency(
        "htmltools-fill",
        "0.0.0.0",
        source={"package": "bslib", "subdir": "htmltools/"},
        stylesheet={"href": "fill.css"},
    )