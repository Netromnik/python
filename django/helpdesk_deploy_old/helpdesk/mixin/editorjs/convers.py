class BaseConverstEdit:
    fields = []

    def __init__(self,json_data):
        ## html_obj = [(type,html_data),]
        self.html_obj = [ (i["type"],getattr(self,i["type"])(i["data"])) for i in json_data['blocks'] if i["type"] in self.fields]

    def get_html(self):
        html = [ '<div class="block {} ">{}</div>'.format(getattr(self,str[0]+"_class"),str[1]) for str in self.html_obj ]
        return "".join(html)

class ConverstEdit(BaseConverstEdit):
    fields = ['header', 'paragraph', 'image']
    header_class = 'header'
    image_class = 'image'
    paragraph_class = 'paragraph'
    def header(self,data):
        level = data["level"]
        text  = data["text"]
        return "<h{}>{}<h{}>".format(level,text,level)

    def paragraph(self,data):
        return "<p>{}<p>".format(data["text"])

    def image(self,data):
        ## ,{"type":"image","data":{"file":{"url":"/.png"},"caption":"Filters","withBorder":false,"stretched":false,"withBackground":false}}
        file_url = data["file"]["url"]
        caption = data["caption"]
        withBorder = data["withBorder"]
        stretched = data["stretched"]
        withBackground = data["withBackground"]
        return "<img src='{}'/>".format(file_url)

json_data = {'time': 1606101651456,
 'blocks': [{'type': 'header',
   'data': {'text': 'Работа с опен впн', 'level': 1}},
  {'type': 'paragraph',
   'data': {'text': 'Hey. Meet the new Editor. On this page you can see it in action — try to edit this text.'}},
  {'type': 'image',
   'data': {'file': {'url': '/media/documents/2020/11/23/all_cases_HAK_CP_2020_bNDltrX.png'},
    'caption': 'Filters',
    'withBorder': False,
    'stretched': False,
    'withBackground': False}}],
 'version': '2.19.0'}

data = ConverstEdit(json_data).get_html()
print(data)