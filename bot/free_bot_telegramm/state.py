from db import TABLE_NAME ,insert,get_row ,update ,delete
import logging

log_d = logging.info

class BaseSteta:
    list_state = []
    model = TABLE_NAME
    state_zero = ''
    session = None
    state = state_zero

    def _create_session(self,user_id:str):
        insert(self.model, {
            "user_id": user_id,
            "state": self.state_zero
        })
        self._is_session(user_id)
        log_d(f"Create sessions {user_id}")

    def _is_session(self,user_id:int)->bool:

        user_id = int(user_id)
        session = get_row(self.model,['user_id','body_text','photo','locate','state'],['user_id', user_id])
        log_d(f"Get session {self.__class__} {user_id} \n {session}")
        if len(session) ==  0 :
            return False
        else:
            self.session = session[0]
            return True

    def __init__(self,user_id:int)->None:
        if self._is_session(user_id) == False:
            self._create_session(user_id)

    def check_state(self,state)->bool:
        log_d(f"Class state: {self.state}\n User state {self.session['state']}")
        if state == self.state:
            return True
        else:
            return False

    def _change_data(self,change_data:dict):
        change_data['state'] = self.state
        log_d(f"Session date {self.session}\nChange data {change_data}")
        update(TABLE_NAME, column_and_data=change_data, conditional=['user_id', self.session['user_id']])

class StateText(BaseSteta):
    state = 'text'
    def get_text(self)->str:
        return self.session['text']

    def set_text(self,text):
        self._change_data({
            'body_text':text
        })

    @property
    def is_text(self,):
        return True

class StatePhoto(BaseSteta):
    state = 'photo'

    def get_photo(self)->list[str]:
        photo = self.session['photo']
        photo_split = photo.split(';')
        log_d(f"Photo date {self.session['photo']}\n Split {photo_split}")
        return photo_split

    def set_photo(self,id_photo:str):
        photo = self.session['photo']
        log_d(f"Set photo {photo} :{photo.__class__} --{id_photo}")
        if photo == None:
            photo = id_photo
        else:
            photo = photo + ";" + id_photo
        self._change_data({
            'photo': photo
        })

    @property
    def is_photo(self,):
        return True


class StateGeo(BaseSteta):
    state = 'geo'
    def get_geo_link(self):
        return self.session['locate']

    def set_geo_link(self,geo:str,type:str):
        log_d("Set locate ")

        self._change_data({
            'locate': "{}:{}".format(type, geo)
        })

    @property
    def is_geo(self):
        if self.session['locate'].split(":")[0] == "cord":
            return True
        else:
            return False

    @property
    def is_geo_text(self):

        if self.session['locate'].split(":")[0] == "text":
            return True
        else:
            return False

def get_state(user_id:str)->BaseSteta:
    state = BaseSteta(user_id).session['state']
    if BaseSteta.state == state:
        return StateText(user_id)
    elif StateText.state == state:
        return StateGeo(user_id)
    elif StateGeo.state == state:
        return StatePhoto(user_id)
    elif StatePhoto.state ==state:
        return StatePhoto(user_id)

def drop_task_state(user_id):
    delete(TABLE_NAME,user_id)
    BaseSteta(user_id)