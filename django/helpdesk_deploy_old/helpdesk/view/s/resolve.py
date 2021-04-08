from django.http import HttpResponseRedirect , HttpResponseNotAllowed

def router(request,slug_query_pk,slug_stream_pk,):
    # support for pre setting view for user
    user = request.user
    if hasattr(request.user,'support_q'):
        url = user.support_q.get_view_type_url(slug_query_pk,slug_stream_pk)
        return HttpResponseRedirect(url)
    else:
        return HttpResponseNotAllowed('Not auch')