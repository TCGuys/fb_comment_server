import time

import openai
from flask import Flask, request, jsonify
import requests
import json


app = Flask(__name__)

import requests
import json

class InvalidToken(Exception):
    pass

# здесь не прикручена пагинация, хз сколько коментов он обрабатывает и сколько постов
class FacebookPostRuner:
    def __init__(self, token : str, site = "graph.facebook.com", version = "v18.0"):
        self.token = "access_token=" + token
        self.site = site if "https://" in site else "https://" + site
        self.version = version
        self.url = f'{self.site}/{version}/'
        self.fields_url = f'{self.site}/{version}/me?fields='

    def get_json_by_str_fields(self, fields = "posts"):
        return requests.get(self.fields_url + fields + "&" + self.token).text

    def get_json_by_id(self, id = "122106155180052382_122101224734052382", sup_param = "/comments"):
        return requests.get(self.url + id + sup_param + "?" + self.token).text

    def get_user_posts_in_list_format(self):
        ''' получаем список постов (!БЕЗ ПАГИНАЦИИ!)'''
        data = json.loads(self.get_json_by_str_fields(fields="posts"))
        if "error" in data.keys():
            raise InvalidToken(str(data["error"]))
        posts_data = data["posts"]["data"]
        return posts_data

    def get_posts_comments(self):
        ''' вызываем отдельно для каждого поста (много малых json)
        список коменатриев (много json чуть побольше) (!БЕЗ ПАГИНАЦИИ!)'''
        id_list = [elem["id"] for elem in self.get_user_posts_in_list_format()]
        return [json.loads(self.get_json_by_id(elem, sup_param = "/comments"))["data"] for elem in id_list]

    def get_posts_comments(self):
        ''' вызываем отдельно для каждого поста (много малых json)
        список коменатриев (много json чуть побольше) (!БЕЗ ПАГИНАЦИИ!)'''
        id_list = [elem["id"] for elem in self.get_user_posts_in_list_format()]
        return [json.loads(self.get_json_by_id(elem, sup_param = "/comments"))["data"] for elem in id_list]

    def valdiate_message_by_chat(self, comments_to_validate, token = "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"):
        ''' валидируем сообщения. Вернется булевый список.'''
        openai.api_key = token

        messages = [{"role": "user", "content": "given an array of comments " + str(
            comments_to_validate) + "For each comment, determine whether it is positive or negative.Give the answer in the form true or false for each comment, start the answer for each comment on a new line. You should only give the answer true or false without any other information, there should be no other text. Mark as negative only comments that are clearly negative"}]

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=messages,
                                                temperature=0.5,
                                                max_tokens=1000)

        request_from_chat = dict(response.to_dict()["choices"][0])["message"]["content"]

        word_only = ["".join(c for c in elem if c.isalnum()).lower() for elem in request_from_chat.split()]

        bool_only = list(filter(lambda x: x == "false" or x == "true", word_only))

        return [elem == "true" for elem in bool_only]

    def only_valid_comments_list(self, comments_lsit, gpt_token = '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'):
        ''' Разделил на разные функции для дальнейшего переиспользования '''
        comments_to_validate = [elem["message"] for elem in comments_lsit]
        print(comments_to_validate)

        bool_list = []

        for sublist in [comments_to_validate[i:i+5] for i in range(0, len(comments_to_validate), 5)]:
            print(sublist)
            while True:
                try:
                    bool_sublist = self.valdiate_message_by_chat(sublist, gpt_token)
                except Exception as e:
                    if "Rate limit reached for" in str(e):
                        time.sleep(80)
                    else:
                        raise e
                print(bool_sublist)
                if len(sublist) == len(bool_sublist):
                    bool_list += bool_sublist
                    break
                elif len(sublist) == 1 and bool_sublist:
                    bool_list += [bool_sublist[0]]
                    break

        problems = []
        for index in range(len(bool_list)):
            if not bool_list[index]:
                problems.append(comments_lsit[index])
        print(problems)

        return problems

    def post_hided_by_list_id(self, comments_lsit = [], hide = False, gpt_token = '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'):
        ''' удаляем комментарии по списку id или просто по id
        можно передавать и не индексированные по id списки, если так будет проще валидировать '''
        non_valid_comments = self.only_valid_comments_list(comments_lsit, gpt_token)

        request_list = []
        for elem in non_valid_comments:
          url = f'{self.site}/{elem["id"]}?is_hidden={str(hide).lower()}&' + self.token
          print(url)
          req = requests.post(url)
          request_list.append((req.text, elem["id"], elem["message"], req.status_code))
        return request_list

@app.route('/process_post_data', methods=['POST'])
def process_post_data():
    print(42)
    # Проверяем, есть ли токен в теле POST-запроса
    try:
        data = request.json

        if 'facebook_token' not in data:
            return jsonify({'error': 'Facebook Token is missing'}), 400  # Возвращаем ошибку, если токен отсутствует

        if 'gpt_token' not in data:
            return jsonify({'error': 'GPT Token is missing'}), 400  # Возвращаем ошибку, если токен отсутствует

        fr_user = FacebookPostRuner(data['facebook_token'])
        all_pages = json.loads(fr_user.get_json_by_str_fields(fields="accounts"))

        all_pages_tokens = [elem["access_token"] for elem in all_pages["accounts"]["data"]]

        to_req_client = []

        for page_token in all_pages_tokens[:1]:
            fr_page = FacebookPostRuner(page_token)
            for comments_in_page in [elem for elem in fr_page.get_posts_comments() if elem]:
                print(comments_in_page)
                to_req_client.append(fr_page.post_hided_by_list_id(comments_lsit = comments_in_page, hide = False, gpt_token=data["gpt_token"]))

        return jsonify({"Succsess": True, "List_of_comments": to_req_client})
    except Exception as err:
        print("ERROR:  " + str(err))
        if str(err) == "accounts":
            return jsonify({"Succsess": False, "error": "error of facebook token"})
        if "Incorrect API key provided" in str(err):
            return jsonify({"Succsess": False, "error": "error of gpt token"})
        return jsonify({"Succsess": False, "error": str(err)})

@app.route('/hello', methods=['get'])
def hello():
    return jsonify("hello")

if __name__ == '__main__':
    app.run(port=5000, debug=True)