from functools import wraps

from django.core.paginator import Paginator
from django.http import Http404


def paginate(per_page=5):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 获取视图函数返回的查询集
            queryset = view_func(request, *args, **kwargs)

            # 创建分页对象
            paginator = Paginator(queryset, per_page)
            page_number = request.GET.get("page")

            try:
                page_obj = paginator.get_page(page_number)
            except Exception:
                # 如果请求页码不合法，抛出404错误
                raise Http404

            # 返回一个包含分页对象的字典，方便在模板中使用
            return {
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
            }

        return _wrapped_view

    return decorator
