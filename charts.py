# Import necessary modules from Flask, pymongo, and os
from flask import Flask, render_template, request, redirect, session, flash
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo as mongo
import os, datetime, altair, pandas, base64

# MongoDB connection URL
url = "mongodb+srv://admin:admin@cluster0.blievi7.mongodb.net/?retryWrites=true&w=majority"
# Create a MongoClient instance with the specified URL and ServerApi version
client = MongoClient(url, server_api=ServerApi('1'))

# Access the 'expotec' database and its collections
db = client["expotec"]
col_users = db["users"]
col_charts = db["charts"]
col_topics = db["topics"]
col_questions = db["questions"]
col_comments = db["comments"]
def update_user_data(session,question,question_awnser):
    col_users.update_one({'user':session},{"$set":{question:question_awnser}})
    col_users.update_one({'user':session,'sub_topic': {'$ne': question}},{'$addToSet':{'ava_topic':question}})
    col_topics.update_one({'topic':question,'sub_topic': {'$ne': question_awnser}},{'$addToSet': {'sub_topic': question_awnser}})

def new_simplify_topics(info):
   
    # add first letter
    oupt = info[0]
     
    # iterate over string
    for i in range(1, len(info)):
        if info[i-1] == ' ':
           
            # add letter next to space
            oupt += info[i]
    oupt = oupt.lower()
    return oupt
def desimplify_topics(info):
    if info == "stt":
        return "Estado onde mora"
    elif info == "hair":
        return "Cor do Cabelo"
    elif info == "shoe":
        return "Numero do Calçado"
    elif info == "cty":
        return "Cidade onde mora"
    else:
        return info
def simplify_topics(info):
    # add first letter
    oupt = info[0]
     
    # iterate over string
    for i in range(1, len(info)):
        if info[i-1] == ' ':
           
            # add letter next to space
            oupt += info[i]
    oupt = oupt.lower()
    return oupt
# Define a user object class to represent user data
class user_obj:
    def __init__(self,user,name,email,pwrd,pwrdconf, pic):
        self.user = user
        self.name = name
        self.email = email
        self.pwrd = pwrd
        self.pwrdconf = pwrdconf
        self.pic = pic

    # Define methods to convert user object to dictionary (JSON) format
    def __dict_user__(self):
        return {
            'email': self.email,
            'user': self.user,
            'password': self.pwrd,
            'name': self.name,
            'profile_img' :self.pic

        }
    def __dict__(self):
        return {
            
        }




# Clear console screen for better visualisation
os.system("cls")

# Create a Flask charts instance and set a secret key to handle sessions
charts = Flask(__name__)
charts.secret_key = 'enzo'



# Define route to render index.html template
@charts.route('/')
def index():
    error_state = request.args.get('error_state', 'hidden')  
    error_message = request.args.get('error_message', '')    
    return render_template('index.html', visible = error_state, error = error_message)

@charts.route('/land')
def land():
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/')
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
    session['user_logged'] = aux_user
    img_pic = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)
    os.system("cls")
    charts_data = col_charts.find()
    titles = []
    types = []
    for aux_charts in charts_data:
        titles.append(aux_charts['title'])
        types.append(aux_charts['type'])
    return render_template('land.html', user_name = session['user_logged'],profile_pic =  img_pic, titles = titles, types = types)

@charts.route('/land/<title>')
def chart_page(title):
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/')
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
    session['user_logged'] = aux_user
    img_pic = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)


    chart_data = col_charts.find_one({"title": title})
    aux_title = chart_data['title']
    aux_creation = chart_data['creation_date']
    aux_author = chart_data['creator']
    aux_type = chart_data['type']
    aux_desc = chart_data['description']
    
    comments = col_comments.find({'chart_name':title})
    comments_array = []
    commenter_array = []
    #commenter_pic_array = []
    for comment in comments:
        comments_array.append(comment['comment'])
        commenter_array.append(comment['user'])
        #commenter_pic_array.append(comment['user_pic'])
        

    if aux_type=="simple":


        os.system("cls")
        aux_topic = chart_data['topic1']
        user_topics = []
        user_data = col_users.find({aux_topic: {'$exists': True}})
        user_topics = [each[aux_topic] for each in user_data]


        df = pandas.DataFrame({'category': user_topics})
        counts = df['category'].value_counts().sort_index()
        chart_df = pandas.DataFrame({'Topic': counts.index, 'Frequency': counts.values})
        chart_df['ratio'] = round((chart_df['Frequency']/len(user_topics)*100))
        pie_chart = altair.Chart(chart_df).mark_arc(size=100).encode(
            theta='ratio:Q',
            color='Topic:N',
            tooltip='Frequency:N'
            
        ).properties(
       width=919,
         height=529,
        title=title
        )
        pie_chart_json = pie_chart.to_json()



        return render_template('chart_page.html',comments = comments_array,commenters = commenter_array, #comenters_pic = commenter_pic_array
                               user_name = session['user_logged'], profile_pic =  img_pic, chart_description = aux_desc, chart_tittle=title,chart_topic = aux_topic, pie_chart_json = pie_chart_json, chart_creation = aux_creation, chart_author = aux_author )
    else:

        if chart_data['topic3'] == "":
            os.system("cls")
            aux_topic = chart_data['topic1']
            aux_topic2 = chart_data['topic2']
            aux_subtopic = chart_data['subtopic2']
            user_topics = []
            user_data = col_users.find({
                '$and': [
                    { aux_topic: { '$exists': True } },
                    { aux_topic2: aux_subtopic }
                ]
            })
            user_topics = [each[aux_topic] for each in user_data]
            df = pandas.DataFrame({'category': user_topics})
            counts = df['category'].value_counts().sort_index()
            chart_df = pandas.DataFrame({'Topic': counts.index, 'Frequency': counts.values})
            chart_df['ratio'] = round((chart_df['Frequency']/len(user_topics)*100))
            pie_chart = altair.Chart(chart_df).mark_arc(size=100).encode(
                theta='ratio:Q',
                color='Topic:N',
                tooltip='Frequency:N'
                
            ).properties(
            width=919,
            height=529,
            title=title
            )

            pie_chart_json = pie_chart.to_json()
            return render_template('chart_page.html',comments = comments_array,commenters = commenter_array, #comenters_pic = commenter_pic_array,
                                   user_name = session['user_logged'],profile_pic =  img_pic, chart_description = aux_desc, chart_tittle=aux_title,chart_topic = desimplify_topics(aux_topic),chart_topic2 = desimplify_topics(aux_topic2), pie_chart_json = pie_chart_json, chart_creation = aux_creation, chart_author = aux_author )
        else:
            os.system("cls")
            aux_topic = chart_data['topic1']
            aux_topic2 = chart_data['topic2']
            aux_topic3 = chart_data['topic3']
            aux_subtopic = chart_data['subtopic2']
            aux_subtopic2 = chart_data['subtopic3']
            user_topics = []
            user_data = col_users.find({
                '$and': [
                    { aux_topic: { '$exists': True } },
                    { aux_topic2: aux_subtopic },
                    { aux_topic3: aux_subtopic2 }
                    
                ]
            })
            user_topics = [each[aux_topic] for each in user_data]
            df = pandas.DataFrame({'category': user_topics})
            counts = df['category'].value_counts().sort_index()
            chart_df = pandas.DataFrame({'Topic': counts.index, 'Frequency': counts.values})
            chart_df['ratio'] = round((chart_df['Frequency']/len(user_topics)*100))
            pie_chart = altair.Chart(chart_df).mark_arc(size=100).encode(
                theta='ratio:Q',
                color='Topic:N',
                tooltip='Frequency:N'
                
            ).properties(
            width=919,
            height=529,
            title=title
            )

            pie_chart_json = pie_chart.to_json()
            return render_template('chart_page.html',comments = comments_array,commenters = commenter_array, #comenters_pic = commenter_pic_array,
                                   user_name = session['user_logged'],profile_pic =  img_pic, chart_description = aux_desc, chart_tittle=aux_title,chart_topic = desimplify_topics(aux_topic),chart_topic2 = desimplify_topics(aux_topic2), pie_chart_json = pie_chart_json, chart_creation = aux_creation, chart_author = aux_author )
        
@charts.route('/comment',methods=['POST','GET',])
def comment():
    comment = request.form['comentario']
    url = request.form['chart_url']
    col_comments.insert_one({'comment':comment,'user':session['user_logged'],'chart_name':url})
    return redirect(request.referrer)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
@charts.route('/criar-chart')
def create_chart():
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
    session['user_logged'] = aux_user
    img_pic = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)
    combo_topics = col_users.find_one({'user':session['user_logged']})
    sub_topics = col_topics.find()
    sub_array = []
    for info in sub_topics:
        sub_array.append(info['sub_topic'])
    return render_template('create_chart.html',user_name = session['user_logged'],profile_pic =  img_pic,topics = combo_topics["ava_topic"], sub_topic = sub_array)

@charts.route('/inserir-chart',methods=['POST',])
def insert_chart():
    
    chart_tittle = request.form['txttitulo']
    chart_date = request.form['txtdata']
    chart_description = request.form['txtdescricao']
    chart_topic1 = request.form['first-select']
    chart_topic2 = request.form['second-select']
    chart_subtopic2 = request.form['second-if-select']

    chart_topic3 = request.form['third-select']
    chart_subtopic3 = request.form['third-if-select']


    if chart_topic2 == "simple":
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"type":"simple","creator":session['user_logged'],'creator_id':session['id']})
    else:
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"topic2":chart_topic2,"subtopic2":chart_subtopic2.lower(),"topic3":chart_topic3,"subtopic3":chart_subtopic3,"type":"complex","creator":session['user_logged'],'creator_id':session['id']})
    return redirect(f'/land/{chart_tittle}')


@charts.route('/profile')
def profile():
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
        aux_email = info['email']
        aux_pass = info['password']
    session['user_logged'] = aux_user
    img_pic = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)
    return render_template('profile.html',user_name = session['user_logged'],password = aux_pass,email = aux_email,profile_pic =  img_pic,name = session['name'],user=session['user_logged'])

@charts.route('/profile/change_pic', methods=['POST',])
def cng_pic():
    pic = request.files['img']
    new_pic = base64.b64encode(pic.read()).decode('utf-8')
    col_users.update_one({'user':session['user_logged']},{'$set':{'profile_img':"data:image/png;base64,"+new_pic}})
    
    return redirect('/profile')


@charts.route('/profile/change_email')
def cng_email():
    return render_template('email.html',user_name = session['user_logged'])
@charts.route('/profile/change_password')
def cng_password():
    return render_template('password.html',user_name = session['user_logged'])

@charts.route('/profile/mycharts')
def mycharts():
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
    session['user_logged'] = aux_user
    img_pic = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)
    mychart = col_charts.find({"creator":session['user_logged']})
    titles = []
    types = []
    for aux_charts in mychart:
        print(aux_charts['title'])
        titles.append(aux_charts['title'])
        types.append(aux_charts['type'])
    return render_template("my_charts.html", chart_title = titles, user_name=session['user_logged'])

@charts.route('/adicionar-informações')
def add_info():
    usercheck = col_users.find({"user":session['user_logged']})
    for info in usercheck:
        aux_user = info['user']
        aux_img = info['profile_img']
        aux_name = info['name']
        aux_id = info['_id']
    session['user_logged'] = aux_user
    img = aux_img
    session['name'] = aux_name
    session['id'] = str(aux_id)
    return render_template('add_info.html', user_name = session['user_logged'],profile_pic =  img)

@charts.route('/inserir-info',methods=['POST',])  
def insert_info():
        
        question_1 = "Animal Favorito"
        question_1_awn=request.form['animal']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Cor Favorita"
        question_1_awn=request.form['cor']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))
        question_1 = "Idade"
        question_1_awn=request.form['idade']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Como veio"
        question_1_awn=request.form['transporte']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Tem pet"
        question_1_awn=request.form['pet']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Musica Favorita"
        question_1_awn=request.form['musica']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Já saiu do país"
        question_1_awn=request.form['pais']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Metros de Altura"
        question_1_awn=request.form['altura']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))
        question_1 = "Quantidade de livros lidos esse ano"
        question_1_awn=request.form['livro_ano']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Já saiu do estado"
        question_1_awn=request.form['estado']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Está trabalhando"
        question_1_awn=request.form['trabalha']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Filme Favorito"
        question_1_awn=request.form['filme']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Genero de Musica"
        question_1_awn=request.form['musica_genero']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Genero de Filme"
        question_1_awn=request.form['filme_genero']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

        question_1 = "Cor dos olhos"
        question_1_awn=request.form['olhos']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Relacionamento romantico"
        question_1_awn=request.form['relacionamento']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Melhor animal de estimação"
        question_1_awn=request.form['melhor_pet']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Achou o site interessante"
        question_1_awn=request.form['interessante']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Quantidade de refeições no dia"
        question_1_awn=request.form['refeicoes']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))


        question_1 = "Quantidade de quartos em casa"
        question_1_awn=request.form['quartos']
        update_user_data(session['user_logged'],question_1.lower(),question_1_awn.lower().strip(" "))

    

        return redirect('/land')
# Define route for registration form submission
@charts.route('/registrar', methods=['POST',])
def regis():
    # Create a new user object with form data
    new_user = user_obj(
        user = request.form['txtusuario'],
        name = request.form['txtnome'],
        email = request.form['txtemail'],
        pwrd = request.form['txtsenha'],
        pwrdconf = request.form['txtsenhaconf'],
        pic = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAABTCAMAAADUbMsyAAABX1BMVEWenp6fn5+goKChoaGioqKjo6OkpKSlpaWmpqanp6eoqKipqamqqqqrq6usrKytrKytra2ura2urq6vrq6vr6+wr6+wsLCxsbGysrKzs7O0tLS1tbW2tra3t7e4uLi5ubm6urq7u7u8vLy9vb2+vr6/v7/AwMDBwcHCwsLDw8PExMTFxcXGxsbHxcXHx8fIxsbIyMjJx8fJycnKyMjKysrLycnLysrLy8vMy8vMzMzNzMzNzc3Ozs7Pzc3Pzs7Pz8/Qz8/Q0NDR0NDR0dHS0tLT0tLT09PU09PU1NTV1NTV1dXW1dXW1tbX1tbX19fY2NjZ2dna2dna2trb29vc29vc3Nzd3d3e3t7f39/g4ODh4ODh4eHi4uLj4+Pk5OTl5eXm5ubn5+fo5+fo6Ojp6Ojp6enq6urr6+vs7Ozt7e3u7u7v7+/w8PDx8fHy8vLz8/P09PT19fX29vb39/f///8Ku0ecAAAAAWJLR0R0322obQAAA19JREFUWMPt2etTElEUAPDDS8FXRaaoFCCpmawmYUpZlpkhEZC0V42XRCTy3uX/n2lfymvvLvcuM02T54POuGd/cx+7O+dcoT36gDvzL5lsPNsancnlCu12wQxg8WVGY9Ze2O2NdmUGpPBVR2CmxgE8rbgDlHDkDZsHomO1QSdseYNmBAbDvl83YDbXTaAWY8fUZsUJuFjh6MyGOmmZEn+u0ZmrqqQ1PC39jtGYuZ61NJktVtuY3fk0jiblnWpQmMu3I1t6fhBLplikhDxOOCI3GxaF9CRRb8zLf3eRm6wy5w3UH17lSp3YDMp3BgZItKlMIENsysv5ZJBECWXzYsTmorQ9CRXzZkE/EJsu3DARCsvmAd04w6ommtV+mDTX05RUNyNW0UwSmyHxXUGYCInblKd6PmdxJnJRPZ9VYShLWFNYmQmK9114rb1apofcvHoM4MeaPuEL2iI2swHha65lhn8TmxdRYShY0wvm00tSkz9j7bCuMU4nypObyA2bGuYaKhDP/RwFYBdrrpiiqERsZlBMuA8Xb5wIXRObReFGhI84Qk1is450Ik3xHmV0zDKFqTPQDE9Th1SKePG8xNHVYDzezFLXivglLVKbJaxZpTax23TO09feaZqp65hldfKsZcDkLyiGqdd31FRXkzPWH2VVzCuDPVf62wB58sugmT887SeZnwbNXOpVrFtkDxnmhyGTC4RQYuv1bRXKnrxkGOaev0Fv1hYgKNTF28zO4ZdE4uvnt9uMGA9g5oq6N7wPoolO95ieEPo7R5HOrIrHAEFpyp+2us2HYhlZojGbc3BjCkN936U+Ei9MVshNXm6DQrfbE323I7nbe1KpD3OkNRhf2pAbgcds94P0PSW0iFHl1MF/yQ1vVmPL9tvm1d3/zB85OmcDnqPyMGYj6jb3NNeOntKBfWbpuWpyfazqmLlV62DLvhDp1DSTg5fNvr7PfrfJJebVTyrMq/Kqsl7MUcbMcVPV5CJT2OMPeatS8/gE+35z0GSnQSvEktmtmeGI8r1m3Q/aYY6hXZ0UWLruNotTevngZfVzxtMdszCumw5j+/o5YDm7MWsTQ6TD4jBJtpJirsBQ6UNlLfCSWTbBCONCMo9HSUJAMkMjNf2SGfyPzXR4lJG6+3/Hv2D+AevXwHEUe10sAAAAAElFTkSuQmCC"
        )
    # Insert user data as a dictionary (JSON file) into the 'users' collection
    col_users.insert_one(new_user.__dict_user__())
    sessao = request.form['txtusuario']
    question_1 = "País em que mora"
    question_1_awn=request.form['txtpais']
    update_user_data(sessao,question_1.lower(),question_1_awn.lower().strip(" "))
    question_1 = "Estado em que mora"
    question_1_awn=request.form['txtestado'] 
    update_user_data(sessao,question_1.lower(),question_1_awn.lower().strip(" "))
    question_1 = "Cidade em que mora"
    question_1_awn=request.form['txtcidade']
    update_user_data(sessao,question_1.lower(),question_1_awn.lower().strip(" "))
    question_1 = "Cor do Cabelo"
    question_1_awn=request.form['txtcorcabelo']
    update_user_data(sessao,question_1.lower(),question_1_awn.lower().strip(" "))
    question_1 = "Numero do calçado"
    question_1_awn=request.form['txtcalcado']
    update_user_data(sessao,question_1.lower(),question_1_awn.lower().strip(" "))

    username = request.form['txtusuario']
    password = request.form['txtsenha']
    # Search the 'users' collection in the database for a user with the specified username
    try:
        usercheck = col_users.find({"user":username})
        # Iterate over the search results (usually just one user document)
        for info in usercheck:
            aux_user = info['user']
            aux_pass = info['password']
            aux_img = info['profile_img']
            aux_name = info['name']
            aux_id = info['_id']
        # Check if the submitted username matches any user in the database
        if username == aux_user:
            # If the username matches, check if the submitted password matches the stored password
            if password == aux_pass:
                # If both username and password match, store the username in the session
                # Redirect the user to the '/land' page (landing page after successful login)
                session['user_logged'] = aux_user
                session['name'] = aux_name
                session['id'] = str(aux_id)
                return redirect('/land')
            else:
                # If the submitted password doesn't match, redirect to the index page (login page)
                return redirect('/')
        else:
            # If the submitted username doesn't match any user in the database, redirect to the index page
            return redirect('/')
    except:
        return redirect('/')

    # Render the index.html template after registration
    return redirect('/land')

# Define route for authentication of user
@charts.route('/logar',methods=['POST',])
# Run the Flask charts
def logar():
  # Retrieve the username and password submitted in the login form
    username = request.form['txtusuariologin']
    password = request.form['txtsenhalogin']
    # Search the 'users' collection in the database for a user with the specified username
    try:
        usercheck = col_users.find({"user":username})
        # Iterate over the search results (usually just one user document)
        for info in usercheck:
            aux_user = info['user']
            aux_pass = info['password']
            aux_img = info['profile_img']
            aux_name = info['name']
            aux_id = info['_id']
        # If the username matches, check if the submitted password matches the stored password
        if password == aux_pass:
            # If both username and password match, store the username in the session
            # Redirect the user to the '/land' page (landing page after successful login)
            session['user_logged'] = aux_user
            session['name'] = aux_name
            session['id'] = str(aux_id)
            return redirect('/land')
        else:
            # If the submitted password doesn't match, redirect to the index page (login page)
            error_state = "visible"
            error_message = "Senha incorreta!"
            return redirect(f'/?error_state={error_state}&error_message={error_message}')
    except:
        error_state = "visible"
        error_message = "Usuario não existe!!"
        return redirect(f'/?error_state={error_state}&error_message={error_message}')

@charts.route('/logout',methods=['POST',])
def logout():
   if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/') 
   session['user_logged'] = None
   return redirect('/')

#charts.run()
