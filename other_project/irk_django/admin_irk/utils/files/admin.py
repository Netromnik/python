def admin_media_static(media_cls):
    """Декоратор для media классов у admin.ModelAdmin

    Сам оборачивает все ссылки на статику в `lazy_static_link`
    !TODO:  Авто
    """

    css = {}
    js = []

    return media_cls
