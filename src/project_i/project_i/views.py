from secrets import token_urlsafe
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone

from .models import User

def home(request):
    user = None
    if request.method == "POST":
        fields={}
        for field_data in request.body.decode('utf-8').split('&'):
            name, value = field_data.split("=")
            fields[name]=value
        print(fields)
        """ CSRF vulnerability!
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
                    if user and user.password == fields["password"]:
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
                new_user = User(
                    login = fields["login"],
                    password = fields["password"],
                    member_since=timezone.now()
                )
                new_user.save()
                request.session["login"] = new_user.login
    

    if request.session.get("login", False):
        user = User.objects.get(login = request.session["login"])
    
    print(str(User.objects.all()))
        
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

