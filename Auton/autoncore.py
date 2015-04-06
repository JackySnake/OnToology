#!/usr/bin/python
import sys, os
from github import Github
from datetime import datetime
from subprocess import call
import string, random
import time
from setuptools.command.setopt import config_file


parent_folder = None
ar2dtool_config_types = ['ar2dtool-taxonomy.conf','ar2dtool-class.conf']
ar2dtool_config = os.environ['ar2dtool_config']
#e.g. ar2dtool_dir = 'blahblah/ar2dtool/bin/'
ar2dtool_dir = os.environ['ar2dtool_dir']
#e.g. home = 'blahblah/temp/'
home = os.environ['github_repos_dir']


ontology_formats = ['.rdf','.owl','.ttl']

g = None


def git_magic(target_repo,user,cloning_repo,changed_files):
    global g
    global parent_folder
    parent_folder = user
    print '############################### magic #############################'
    #so the tool user can takeover and do stuff
    username = os.environ['github_username']
    password = os.environ['github_password']
    g = Github(username,password)    
    local_repo = target_repo.replace(target_repo.split('/')[-2] ,'AutonUser')
    delete_repo(local_repo)
    #print 'repo deleted'
    fork_repo(target_repo,username,password)
    print 'repo forked'
    clone_repo(cloning_repo,user)
    print 'repo cloned'
#     update_readme(changed_files,cloning_repo,user)
#     print 'readme updated'
    auton_conf = get_auton_configuration()
    print str(auton_conf)
    if auton_conf['ar2dtool_enable']:
        print 'ar2dtool_enable is true'
        draw_diagrams(changed_files)
        print 'diagrams drawn'
    else: 
        print 'ar2dtool_enable is false'
    if auton_conf['widoco_enable']:
        print  'widoco_enable is true'
        generate_widoco_docs(changed_files)
        print 'generated docs'
    else:
        print  'widoco_enable is false'
    if auton_conf['oops_enable']:
        print 'oops_enable is true'
        oops_ont_files(changed_files)
        print 'oops checked ontology for pitfalls'
    else:
        print 'oops_enable is false'
    commit_changes()
    print 'changes committed'
    remove_old_pull_requests(target_repo)
    r = send_pull_request(target_repo,'AutonUser')
    print 'pull request is sent'
    return r



def delete_repo(local_repo):
    try:
        g.get_repo(local_repo).delete()
        print 'repo deleted '
    except:
        print 'the repo doesn\'t exists [not an error]'



def fork_repo(target_repo,username,password):
    time.sleep(5)#the wait time to give github sometime so the repo can be forked successfully
    #this is a workaround and not a proper way to do a fork
    comm = "curl --user \"%s:%s\" --request POST --data \'{}\' https://api.github.com/repos/%s/forks" % (username,password,target_repo)
    call(comm,shell=True)
    print 'fork'
    
    


def clone_repo(cloning_repo,user):    
    time.sleep(5)#the wait time to give github sometime so the repo can be cloned
    print "rm"," -Rf "+home+parent_folder
    call("rm"+" -Rf "+home+parent_folder, shell=True)
    print "git"+" clone"+" "+cloning_repo+" "+home+parent_folder
    call("git"+" clone"+" "+cloning_repo+" "+home+parent_folder, shell=True)
    print "chmod 777 -R "+home+parent_folder
    call("chmod 777 -R "+home+parent_folder, shell=True)



                
def update_readme(changed_files,cloning_repo,user):
    for i in range(3):
        try:
            f = open(home+parent_folder+"/"+"README.md","a")
            break
        except IOError:
            print 'readme is not ready: '+str(i)
            time.sleep(5)
            clone_repo(cloning_repo,user)
    f.write("\n##Changelog "+str(datetime.today())+"\n")
    for chf in changed_files:
        f.write("\n* "+chf)                
    f.close()
                




def commit_changes():
    gu = ""
    gu = "git config  user.email \"ahmad88csc@gmail.com\";"
    gu+="git config  user.name \"AutonUser\" ;"
    #print "command: "+"cd "+home+parent_folder+";"+gu+" git add README.md "    
    #call("cd "+home+parent_folder+";"+gu+" git add README.md ",shell=True)
    print "command: "+"cd "+home+parent_folder+";"+gu+" git add . "    
    call("cd "+home+parent_folder+";"+gu+" git add . ",shell=True)
    print "cd "+home+parent_folder+";"+gu+" git commit -m 'automated change' "
    call("cd "+home+parent_folder+";"+gu+" git commit -m 'automated change' ",shell=True)
    gup =""
    gup = "git config push.default matching;"
    print "cd "+home+parent_folder+";"+gu+gup+" git push "
    call("cd "+home+parent_folder+";"+gu+gup+" git push ",shell=True)







def refresh_repo(target_repo):
    local_repo = target_repo.split('/')[-1]
    g.get_user().get_repo(local_repo).delete()
    g.get_user().create_fork(target_repo)




def remove_old_pull_requests(target_repo):
    title = 'AutonTool update'
    for p in g.get_repo(target_repo).get_pulls():
        if p.title == title:
            p.edit(state="closed")
    



def send_pull_request(target_repo,username):
    title = 'AutonTool update'
    body = title
    err = ""
    for i in range(3):
        try:
            g.get_repo(target_repo).create_pull(head=username+':master',base='master',title=title,body=body)
            #return 'pull request created successfully'
            return {'status': True, 'msg':'pull request created successfully' }
        except Exception as e:
            err = str(e.data)
            print 'pull('+str(i)+'): '+err
            time.sleep(3)
    #return err
    return {'status': False, 'error': err}



def webhook_access(client_id,redirect_url):
    scope = 'admin:org_hook'
    scope+=',admin:org,admin:public_key,admin:repo_hook,gist,notifications,delete_repo,repo_deployment,repo,public_repo,user,admin:public_key'
    sec = ''.join([random.choice(string.ascii_letters+string.digits) for _ in range(9)])
    return "https://github.com/login/oauth/authorize?client_id="+client_id+"&redirect_uri="+redirect_url+"&scope="+scope+"&state="+sec, sec






def add_webhook(target_repo,notification_url):
    name = "web"
    active = True
    events = ["push"]
    config = {
               "url": notification_url,
               "content_type": "form"
    }
    try:
        g.get_repo(target_repo).create_hook(name,config,events,active)
        return {'status': True}
    except Exception as e:
        return {'status': False, 'error': e.data}



def add_collaborator(target_repo,user):
    try:
        msg = g.get_repo(target_repo).add_to_collaborators(user)
        return {'status': True, 'msg': str(msg) }
    except Exception as e:
        return {'status': False, 'error': e.data}



def update_g(token):
    global g
    g = Github(token)



##########################~~~~~~~~~~~~##################################
##########################  ar2dtool   #################################
##########################~~~~~~~~~~~~~#################################


def draw_diagrams(rdf_files):
    print str(len(rdf_files))+' changed files'
    for r in rdf_files:
        #print r+' is changed '
        if r[-4:] in ontology_formats:
            for t in ar2dtool_config_types:
                draw_file(r,t)
        else:
            pass
            #print r+' is not an rdf'




def get_ar2dtool_config(config_type):
    f = open(ar2dtool_config+'/'+config_type,"r")
    return f.read()






def draw_file(rdf_file,config_type):
    outtype="png"
    abs_dir = home+parent_folder+'/'+'drawings'+'/'+config_type+'/'
    config_file = abs_dir+config_type
    directory = ""
    if len(rdf_file.split('/'))>1:
        directory = '/'.join(rdf_file.split('/')[0:-1])
        if not os.path.exists(abs_dir+directory):
            os.makedirs(abs_dir+directory)
    try:
        open(config_file,"r")
    except IOError:
        if not os.path.exists(abs_dir):
            os.makedirs(abs_dir)
        f = open(config_file,"w")
        f.write(get_ar2dtool_config(config_type))
        f.close()
    except Exception as e:
        print 'in draw_file: exception opening the file: '+str(e)
    comm = 'java -jar '
    comm+= ar2dtool_dir+'ar2dtool.jar -i '
    comm+= home+parent_folder+'/'+rdf_file+' -o '
    comm+= abs_dir+rdf_file+'.'+outtype+' -t '+outtype+' -c '+config_file+' -GV -gml '
    print comm
    call(comm,shell=True)
# draw_file('myrdfs/sample.rdf')


########################################################################
############################# Widoco ###################################
########################################################################


#e.g. widoco_dir = 'blahblah/Widoco/JAR/'
widoco_dir = os.environ['widoco_dir']
widoco_config = ar2dtool_config+'/'+'widoco.conf'


def get_widoco_config():
    f = open(widoco_config,"r")
    return f.read()



def generate_widoco_docs(changed_files):
    for r in changed_files:
        if r[-4:] in ontology_formats:
            print 'will widoco '+r
            create_widoco_doc(r)
        else:
            pass
            #print r+' does not belong to supported ontology formats for widoco'




def create_widoco_doc(rdf_file):
    abs_dir = home+parent_folder+'/'+'docs'+'/'
    config_file = abs_dir+rdf_file.split('/')[-1]+'.widoco.conf'
    directory = ""
    if len(rdf_file.split('/'))>1:
        directory = '/'.join(rdf_file.split('/')[0:-1])
        if not os.path.exists(abs_dir+directory):
            os.makedirs(abs_dir+directory)
    try:
        open(config_file,"r")
    except IOError:
        if not os.path.exists(abs_dir):
            os.makedirs(abs_dir)
        f = open(config_file,"w")
        f.write(get_widoco_config())
        f.close()
    except Exception as e:
        print 'in create_widoco_doc: exception opening the file: '+str(e)
    comm = "cd "+home+parent_folder+"; "
    comm+= "java -jar "
    comm+=widoco_dir+"widoco-0.0.1-jar-with-dependencies.jar "
    comm+=" -ontFile "+home+parent_folder+'/'+rdf_file
    comm+=" -outFolder "+abs_dir+directory
    comm+=" -confFile "+config_file
    print comm
    call(comm,shell=True)
    

########################################################################
######################  Auton configuration file  ######################
########################################################################

import ConfigParser

def get_auton_configuration():
    print 'auton config is called'
    config = ConfigParser.RawConfigParser()
    ar2dtool_sec_name = 'ar2dtool'
    widoco_sec_name = 'widoco'
    oops_sec_name = 'oops'
    ar2dtool_enable = True
    widoco_enable = True
    oops_enable = True
    opened_conf_files = config.read(home+parent_folder+'/auton.cfg')
    if len(opened_conf_files) == 1:
        print 'auton configuration file exists'
        print opened_conf_files[0]
        try:
            ar2dtool_enable = config.getboolean(ar2dtool_sec_name,'enable')
            print 'got ar2dtool enable value'
        except:
            print 'ar2dtool enable value doesnot exist'
            pass
        try:
            widoco_enable = config.getboolean(widoco_sec_name, 'enable')
            print 'got widoco enable value'
        except:
            print 'widoco enable value doesnot exist'
            pass
        try:
            oops_enable = config.getboolean(oops_sec_name, 'enable')
            print 'got oops enable value'
        except:
            print 'oops enable value doesnot exist'
    else:  
        print 'auton configuration file does not exists'
        config.add_section(ar2dtool_sec_name)
        config.set(ar2dtool_sec_name, 'enable', ar2dtool_enable) 
        config.add_section(widoco_sec_name)
        config.set(widoco_sec_name,'enable',widoco_enable)
        config.add_section(oops_sec_name)
        config.set(oops_sec_name,'enable',oops_enable)
        conff = home+parent_folder+'/auton.cfg'
        print 'will create conf file: '+ conff
        try:
            with open(conff, 'wb') as configfile:
                config.write(configfile)
        except Exception as e:
            print 'expection: '
            print e
    return {'ar2dtool_enable':ar2dtool_enable , 'widoco_enable': widoco_enable, 'oops_enable': oops_enable}




############################---------###################################
############################  OOPS!  ###################################
############################\_______/###################################
import urllib2

def valid_ont_file(r):
    if r[-4:] in ontology_formats:
        return True
    return False


def oops_ont_files(changed_files):
    for r in changed_files:
        if valid_ont_file(r):
            print 'will oops: '+r
            get_pitfalls(home+parent_folder+'/'+r) 



def get_pitfalls(ont_file):
    f = open(ont_file,'r')
    ont_file_content = f.read()
    url = 'http://oops-ws.oeg-upm.net/rest'
    xml_content = """
    <?xml version="1.0" encoding="UTF-8"?>
    <OOPSRequest>
          <OntologyUrl></OntologyUrl>
          <OntologyContent>%s</OntologyContent>
          <Pitfalls></Pitfalls>
          <OutputFormat></OutputFormat>
    </OOPSRequest>    
    """ %(ont_file_content)
    req = urllib2.Request(url, xml_content)
    req.add_header('Content-Type', 'application/xml; charset=utf-8')
    req.add_header('Content-Length', len(xml_content))
    oops_reply = urllib2.urlopen(req)
    print 'OOPS! reply:  '+oops_reply.read()


