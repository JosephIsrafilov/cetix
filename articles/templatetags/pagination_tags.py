from django import template

register = template.Library()


@register.simple_tag
def elided_page_range(paginator, current_page, on_each_side=2, on_ends=1):


    if paginator is None:
        return []
    try:
        return paginator.get_elided_page_range(
            number=current_page,
            on_each_side=on_each_side,
            on_ends=on_ends,
        )
    except Exception:
        return paginator.page_range

