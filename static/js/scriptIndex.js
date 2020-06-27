
/***********
*  Registar e Login
************/

function register() {
    var form = document.getElementById("formRegister");
    var name = form.inputName.value;
    var username = form.inputUsername.value;
    var email = form.inputEmail.value;
    var password = form.inputPassword.value;
    var req = new XMLHttpRequest();
    req.open("POST", "/api/user/register/");
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
     });
    req.send(JSON.stringify({"name":name, "username":username, "email": email, "password": password }));
    form.inputName.value = "";
    form.inputUsername.value = "";
    form.inputEmail.value = "";
    form.inputPassword.value = "";
}

function logout(){
    userlogado = "";
     var req = new XMLHttpRequest();
     sessionStorage.clear();
    req.open("GET", "/api/user/logout");
    req.setRequestHeader('Content-Type', 'application/json');
    req.send();
    checkPages();
}

function login() {
    var form = document.getElementById("formLogin");
    var username = form.inputUsernameLogin.value;
    var password = form.inputPasswordLogin.value;
    let req = new XMLHttpRequest();
    req.open("POST", "/api/user/login");
    userlogado = btoa(username + ':'+ password);
    document.getElementById('userLoggedArea').innerHTML = username;
    req.setRequestHeader('Content-Type', 'application/json');
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
     req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500" || status == "403") {
            window.location.href = "/api/";
            return false;
        }
        else {

        var jsonResponse = JSON.parse(req.response);
        sessionStorage.setItem("id", jsonResponse["session"]);
        sessionStorage.setItem("user", userlogado);
        form.inputUsernameLogin.value = "";
        form.inputPasswordLogin.value = "";
        getProjects();
        }
     });
         req.send(JSON.stringify({'username': username, 'password': password}));
}


/***********
*  Projects
************/
function getAlertSuccess(message){
 document.getElementById('successDialog').style.display = "block";
 document.getElementById('successInformation').innerHTML = message;
}

function getAlertWarnning(message){
 document.getElementById('warningDialog').style.display = "block";
 document.getElementById('warningInformation').innerHTML = message;
}

function getAlertSuccessUser(message){
 document.getElementById('successDialogUser').style.display = "block";
 document.getElementById('successInformationUser').innerHTML = message;
}

function getAlertWarnningUser(message){
 document.getElementById('warningDialogUser').style.display = "block";
 document.getElementById('warningInformationUser').innerHTML = message;
}

function getProjects() {
    var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/");
    req.setRequestHeader('Content-Type', 'application/json');
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.addEventListener("load", function() {
        var projects = JSON.parse(this.responseText);
        var table = document.getElementById('tableProjects');
        var tableBody = document.createElement('TBODY');
        table.appendChild(tableBody);
        var k = '<tbody>';
        var table = document.getElementById('tbodyTableCreateProjects')
        for (var i in projects) {
            k+= '<tr >';
            k+= '<td>' + projects[i].id + '</td>';
            k+= '<td>' + projects[i].title + '</td>';
            k+= '<td>' + projects[i].creation_date + '</td>';
            k+= '<td>' + projects[i].last_updated + '</td>';
            k+= '<td><form class="formsTables">';
            k+= '<button type="button" class="button smallButton whiteHomeForm" onclick="openModalEditProjects(\''+ projects[i].id + '\',\'' + projects[i].title + '\')"';
            k+= ' value="'+ projects[i].id + '"';
            k+= '><i class="fas fa-edit"></i></button>';
            k+= '</form>';
            k+= '<form class="formsTables">';
            k+= '<button type="button" class="button smallButton cancelButtonHome" onclick="openModalDeleteProjects(\''+ projects[i].id + '\')"';
            k+= ' value="'+ projects[i].id + '"';
            k+=' ><i class="fas fa-eraser"></i></button>';
            k+= '</form></td>';
            k+= '<td><button type="button" class="button whiteHomeForm" onclick="getTasks('+ projects[i].id +')">Tarefas</button></td>';
            k+= '</tr>';
        }
         k +='</tbody>';
         table.innerHTML = k;
    });
    checkPages('inicial');
    req.send();
}

function insertProject() {
    var form = document.getElementById("formCreateProjects");
    var title = form.inputTitleProject.value;
    var creationDate = new Date().toISOString().slice(0, 10);
    var lastUpdated = "";
    var req = new XMLHttpRequest();
    req.open("POST", "/api/projects/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     });
     var response = req.send(JSON.stringify({"title": title, "creation_date": creationDate, "last_updated": lastUpdated}));
     $('#modalCreateProjects').modal('hide');
     form.inputTitleProject.value = "";
     getProjects();
     getAlertSuccess('Projeto inserido com successo');
}

function openModalEditProjects(id){
$('#modalEditProjects').modal('show');
var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/"+ id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var project = JSON.parse(this.responseText);
         document.getElementById('inputEditTitleProject').value = project.title;
         document.getElementById('inputHiddenEditProject').value = project.id;
    });
     req.send();
}

function openModalDeleteProjects(id){
$('#modalDeleteProjects').modal('show');
var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/"+ id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var project = JSON.parse(this.responseText);
         document.getElementById('inputDeleteProject').innerHTML = '<b>' + project.title + '</b> ?';
         document.getElementById('inputHiddenDeleteProject').value = project.id;
    });
     req.send();
}

function editProject(){
    var form = document.getElementById("formEditProjects");
    var title = form.inputEditTitleProject.value;
    var id = form.inputHiddenEditProject.value;
    var lastUpdated = new Date().toISOString().slice(0, 10);
    var req = new XMLHttpRequest();
    req.open("PUT", "/api/projects/" + id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
    var response = req.send(JSON.stringify({"title": title, "last_updated": lastUpdated}));
     $('#modalEditProjects').modal('hide');
     form.inputEditTitleProject.value = "";
     getProjects();
     getAlertSuccess('Projecto editado com sucesso');
     form.inputEditTitleProject.value = "";
}

function deleteProject(){
    var form = document.getElementById("formDeleteProjects");
    var id = form.inputHiddenDeleteProject.value;
    var req = new XMLHttpRequest();
    req.open("DELETE", "/api/projects/" + id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
    var response = req.send();
    $('#modalDeleteProjects').modal('hide');
    getProjects();
    getAlertSuccess('Projecto apagado com sucesso');
}


/***********
*  TASKS
************/

function getTasks(project_id){
    var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/" + project_id + "/tasks/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    document.getElementById('tasks-div').style.display = "block";
    req.addEventListener("load", function() {
     document.getElementById('tableTasksDiv').style.display = "None";
     document.getElementById('tableTasks').style.display = "block";
        var tasks = JSON.parse(this.responseText);
        if (tasks != ""){
        var table = document.getElementById('tableTasks');
        var k = '';
        var table = document.getElementById('tbodyTableCreateTasks');
        for (var i in tasks) {
            k+= '<tr>';
            k+= '<td>' + tasks[i].id + '</td>';
            k+= '<td>' + tasks[i].title + '</td>';
            k+= '<td>' + tasks[i].creation_date + '</td>';
            if(tasks[i].completed == "0" ){
            k+= '<td> <button type="button" class="btn btn-success" onclick="openModalCompleteTask(\''+ tasks[i].project_id + '\',\'' + tasks[i].id + '\')">Concluír</button></td>';
            }else {
            k+= '<td>Tarefa Concluída</td>';
            }
            k+= '<td><form class="formsTables">';
            k+= '<button type="button" class="button smallButton whiteHomeForm" onclick="openModalEditTasks(\''+ tasks[i].project_id + '\',\'' + tasks[i].id + '\')"';
            k+= ' value="'+ tasks[i].id + '"';
            k+= '><i class="fas fa-edit"></i></button>';
            k+= '</form>';
            k+= '<form class="formsTables">';
            k+= '<button type="button" class="button smallButton cancelButtonHome" onclick="openModalDeleteTasks(\''+ tasks[i].project_id + '\',\'' + tasks[i].id + '\')"';
            k+= ' value="'+ tasks[i].id + '"';
            k+=' ><i class="fas fa-eraser"></i></button>';
            k+= '</form></td>';
            k+= '</tr>';
        }
         table.innerHTML = k;
        } else {
        document.getElementById('tableTasksDiv').style.display = "block";
        document.getElementById('tableTasks').style.display = "None";
        }

    });
    document.getElementById("currentProjectId").value = project_id;
    req.send();
}

function insertTask() {
    var project_id = document.getElementById("currentProjectId").value;
    var form = document.getElementById("formCreateTasks");
    var title = form.inputTitleTask.value;
    var creationDate = new Date().toISOString().slice(0, 10);
    var completed = 0;
    var req = new XMLHttpRequest();
    req.open("POST", "/api/projects/" + project_id + "/tasks/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     });
     var response = req.send(JSON.stringify({"title": title, "creation_date": creationDate, "completed": completed}));
      $('#modalCreateTasks').modal('hide');
     getTasks(project_id);
     getAlertSuccess('Tarefa inserida com successo');
     form.inputTitleTask.value = "";
}

function openModalEditTasks(id, task_id){
$('#modalEditTasks').modal('show');
var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/"+ id + "/tasks/" + task_id);
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var task = JSON.parse(this.responseText);
         document.getElementById('inputEditTitleTask').value = task.title;
         document.getElementById('inputHiddenEditTask').value = task.id;
    });
     req.send();
}



function openModalCompleteTask(id, task_id){
$('#modalCompleteTask').modal('show');
var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/"+ id + "/tasks/" + task_id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var task = JSON.parse(this.responseText);
         document.getElementById('inputCompleteTask').innerHTML = '<b>' + task.title + '</b> ?';
         document.getElementById('inputHiddenCompleteTask').value = task.id;
    });
     var response = req.send();
}

function completeTask(){
    var project_id = document.getElementById("currentProjectId").value;
    var form = document.getElementById("formCompleteTask");
    var id = document.getElementById("inputHiddenCompleteTask").value;
    var req = new XMLHttpRequest();
    req.open("PUT", "/api/projects/" + project_id + "/tasks/" + id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
     var response = req.send(JSON.stringify({"completed": 1}));
     $('#modalCompleteTask').modal('hide');
     getTasks(project_id);
     getAlertSuccess('Tarefa concluída com successo');
}

function openModalDeleteTasks(id, idTask){
$('#modalDeleteTasks').modal('show');
var req = new XMLHttpRequest();
    req.open("GET", "/api/projects/"+ id + "/tasks/" + idTask + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var task = JSON.parse(this.responseText);
         document.getElementById('inputDeleteTask').innerHTML = '<b>' + task.title + '</b> ?';
         document.getElementById('inputHiddenDeleteTask').value = task.id;
    });
     req.send();

}

function editTask(){
    var project_id = document.getElementById("currentProjectId").value;
    var form = document.getElementById("formEditTasks");
    var title = form.inputEditTitleTask.value;
    var id = form.inputHiddenEditTask.value;
    var req = new XMLHttpRequest();
    req.open("PUT", "/api/projects/" + project_id + "/tasks/" + id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
     var response = req.send(JSON.stringify({"title": title}));
     $('#modalEditTasks').modal('hide');
     getTasks(project_id);
     getAlertSuccess('Tarefa editada com successo');
     form.inputEditTitleTask.value = "";
}

function deleteTask(){
    var project_id = document.getElementById("currentProjectId").value;
    var form = document.getElementById("formDeleteTasks");
    var id = form.inputHiddenDeleteTask.value;
    var req = new XMLHttpRequest();
    req.open("DELETE", "/api/projects/" + project_id + "/tasks/" + id + "/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
    var response = req.send();
    $('#modalDeleteTasks').modal('hide');
    getTasks(project_id);
    getAlertSuccess('Tarefa apagada com successo');
}

function checkPages(page){
if(userlogado == "") {
document.getElementById("login-page").style.display = "block";
document.getElementById("mainmenu-area-top").style.display = "None";
document.getElementById("main-page-projects").style.display = "None";
document.getElementById('tasks-div').style.display = "None";
document.getElementById('tableTasksDiv').style.display = "None";
document.getElementById('usersAccount').style.display ="None";
} else if(page == "inicial"){
document.getElementById("login-page").style.display = "none";
document.getElementById("main-page-projects").style.display = "block";
document.getElementById("mainmenu-area-top").style.display = "block";
document.getElementById('usersAccount').style.display ="None";
document.getElementById('successDialog').style.display = "None";
document.getElementById('warningDialog').style.display = "None";
document.getElementById('tasks-div').style.display = "None";
}
else {
document.getElementById("login-page").style.display = "none";
document.getElementById("main-page-projects").style.display = "none";
document.getElementById('usersAccount').style.display ="block";
document.getElementById("tasks-div").style.display = "none";
document.getElementById('successDialogUser').style.display = "None";
document.getElementById('warningDialogUser').style.display = "None";

}
}


/***********
*  User Information
************/

function editUserInformations(){
    var user_id = document.getElementById("idEditInformationUser").value;
    var form = document.getElementById("userEditInformations");
    var name = form.nameEditInformationUser.value;
    var email = form.emailEditInformationUser.value;
    var username = form.usernameEditInformationUser.value;
    var password = form.passwordEditInformationUser.value;
    var req = new XMLHttpRequest();
    req.open("PUT", "/api/user/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function(){
        var status = req.status;
        if (status == "500") {
            return false;
     }
     }
     );
     document.getElementById('userLoggedArea').innerHTML = name;
     var response = req.send(JSON.stringify({"name": name, "email": email, "username": username, "password": password}));
     disabledUserEdit();
     getAlertSuccessUser('Utilizador editado com sucesso');
}


function showUserDetails(){
    checkPages('userDetails');
    var req = new XMLHttpRequest();
    req.open("GET", "/api/user/");
    req.setRequestHeader('Authorization', 'Basic ' + userlogado);
    req.setRequestHeader('Content-Type', 'application/json');
    req.addEventListener("load", function() {
         var user = JSON.parse(this.responseText);
         document.getElementById('editInformationsUserDiv').style.display ="none";
         document.getElementById('idUserArea').innerHTML = '<input type="hidden" id="idEditInformationUser" value="' + user.id  + '">';
         document.getElementById('nameUserArea').innerHTML = '<input type="text" id="nameEditInformationUser" placeholder="' + user.name + '" value="' + user.name  + '" disabled=true>';
         document.getElementById('emailUserArea').innerHTML = '<input type="text" id="emailEditInformationUser"  placeholder="' + user.email + '" value="' + user.email  + '" disabled=true>';
         document.getElementById('usernameUserArea').innerHTML = '<input type="text" id="usernameEditInformationUser"  placeholder="' + user.username + '" value="' + user.username  + '" disabled=true>';
         document.getElementById('passwordUserArea').innerHTML = '<input type="password" id="passwordEditInformationUser" value="' + user.password  + '" disabled=true>';
         document.getElementById('changeInformationsUserDiv').style.display = "block";
    });
     req.send();
}

function changeInformations(){
         document.getElementById('editInformationsUserDiv').style.display ="block";
         document.getElementById('changeInformationsUserDiv').style.display = "none";
         document.getElementById('nameEditInformationUser').disabled = false;
         document.getElementById('emailEditInformationUser').disabled = false;
         document.getElementById('usernameEditInformationUser').disabled = true;
         document.getElementById('passwordEditInformationUser').disabled = false;
}

function disabledUserEdit(){
    document.getElementById('editInformationsUserDiv').style.display = "None";
         document.getElementById('changeInformationsUserDiv').style.display = "block";
         document.getElementById('nameEditInformationUser').disabled = true;
         document.getElementById('emailEditInformationUser').disabled = true;
         document.getElementById('usernameEditInformationUser').disabled = true;
         document.getElementById('passwordEditInformationUser').disabled = true;
}


if(sessionStorage.getItem("id") != null)
{
var userlogado = sessionStorage.getItem("user")
checkPages('inicial');
getProjects();
}
else{
var userlogado = "";
checkPages('');
}














