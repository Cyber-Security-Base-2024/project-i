from secrets import token_urlsafe
from bcrypt import gensalt, hashpw, checkpw
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import DetailView
from django.db import connection

from .models import User

def home(request):
    user = None
    if request.method == "POST":
        fields={}
        for field_data in request.body.decode('utf-8').split('&'):
            name, value = field_data.split("=")
            fields[name]=value
        print(fields)
        """ CSRF vulnerability.
        Forms needs to have token that is checked against when processing
        request
        
        To fix add CSRF marked codeblocks. Forms have aldeady input elements
        for the token.
        """
        """ CSRF
        if fields["csrf"] != request.session.get("csrf"):
            request.session.flush()
            return redirect("/")
        """
        match fields["action"]:
            case "login":
                try:
                    user = User.objects.get(login = fields["login"])
                    """ HASH
                    if checkpw(
                            fields["password"].encode('utf-8'),
                            user.password.encode('utf-8') ):
                    """
                    if user.password == fields["password"]:
                        request.session["login"] = fields["login"]
                except User.DoesNotExist:
                    return redirect("/")
            case "logout":
                if request.session.get("login", False):
                    del request.session["login"]
            case "create_page":
                request.session["create_user"] = True
            case "create":
                if fields["password"] != fields["repeat"]:
                    return redirect("/")
                    
                password = fields["password"]
                """ OWASP Top 10: A02:2021-Cryptographic Failures
                
                In this case plaintext passwords are saved in database.
                Absolutely bad idea as still many uses same paswords through out the
                internet. So possible leak compomises other sites also.
                
                To fix use hashing: (marked as HASH in out commented code)

                password = hashpw(
                    fields["password"].encode('utf-8'),
                    gensalt() ).decode('utf-8')
                """
                
                    
                sql_command = f"""
                    INSERT INTO project_i_user (login, password, member_since)
                    VALUES (
                        "{fields["login"]}",
                        "{password}",
                        {timezone.now().timestamp()}
                    );
                """
                connection.cursor().execute( sql_command )
                
                """ OWASP Top 10: A03:2021-Injection
                
                Running SQL queries where user can inject control characters
                is absolute suicide. To mitigate give argument as separate
                variables not as text.
                
                To fix:
                new_user = User(
                    login = fields["login"],
                    password = password,
                    member_since=timezone.now()
                )
                new_user.save()
                """
                request.session["login"] = fields["login"]
                
    

    if request.session.get("login", False):
        user = User.objects.get(login = request.session["login"])
    
    csrf = 0
    """ CSRF
    csrf = token_urlsafe(16)
    request.session["csrf"] = csrf
    """
    if user:
        member_list = "<br>".join([u.login for u in User.objects.all()])
        return HttpResponse(members(csrf, user.login, member_list))
    elif request.session.get("create_user", False):
        del request.session["create_user"]
        return HttpResponse(create(csrf))
    else:
        return HttpResponse(login(csrf))


def login( csrf = 0 ):
    return f"""
<html><body>
    <form method="post">
        <label>Login:</label>
        <input type="text" name="csrf" value="{csrf}" hidden>
        <input type="text" name="action" value="login" hidden>
        <input type="text" name="login">
        <br>
        <label>Password:</label>
        <input type="text" name="password">
        <br>
        <input type="submit" value="Login">
    </form>
    <form method="post">
        <input type="text" name="csrf" value="{csrf}" hidden>
        <input type="text" name="action" value="create_page" hidden>
        <input type="submit" value="Create">
    </form>        
</body></html>
"""


def members( csrf = 0, login="", member_list="" ):
    return f"""
<html><body>
    <h1>Members only! Welcome {login}</h1>
    <form method="post">
        <input type="text" name="csrf" value="{csrf}" hidden>
        <input type="text" name="action" value="logout" hidden>
        <input type="submit" value="Logout">
    </form>
    <h2>Member list:</h2>
    {member_list}    
</body></html>
"""

def create( csrf = 0 ):
    return f"""
<html><body>
    <form method="post">
        <label>Create account:</label>
        <input type="text" name="csrf" value="{csrf}" hidden>
        <input type="text" name="action" value="create" hidden>
        <input type="text" name="login">
        <br>
        <label>Password:</label>
        <input type="text" name="password">
        <br>
        <label>Repeat:</label>
        <input type="text" name="repeat">
        <br>
        <input type="submit" value="Create">
    </form>
</body></html>
"""

def user_detail(request, login):
    """ OWASP Top 10: A01:2021-Broken Access Control
    
    Data should not be accessible without properly established session.
    
    To fix:
    
    if not request.session.get("login", False):
        return redirect("/")
    """
    try:
        user = User.objects.get(login = login)
        return HttpResponse(f"""
<html><body>
    Login: {user.login}
    <br>
    Member since: {user.member_since}
</body></html>
""")
    except User.DoesNotExist:
        return redirect("/")
