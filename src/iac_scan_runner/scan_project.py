import pymongo
import bson.json_util as json_util
from bson.json_util import dumps
import json
from datetime import datetime
import os
import uuid

class ScanProject:
    def __init__(self):
        """
        Initialize new user config result database, collection and client
        """        
        self.connect_db()
                
                 
    def connect_db(self):
        """
        Initialize new project collection connection into scan result database
        """
                        
        try:
            connection_string = os.environ['MONGODB_CONNECTION_STRING']  
            
            if connection_string:
                self.myclient = pymongo.MongoClient(connection_string)
                self.mydb = self.myclient["scandb"]
                self.mycol = self.mydb["projects"]
                self.connection_problem = False
        
        # TODO: Consider more specific exceptions     
        except Exception as e:
            print("Project persistence not available")
            print(str(e))
            self.myclient = None
            self.mydb = None
            self.mycol = None
            self.connection_problem = True


    def parse_json(self, data):
        return json.loads(json_util.dumps(data))

    def insert_project(self, result: dict):
        """Inserts new project into database
        :param result: Dictionary holding the project info
        """     
        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(self.parse_json(result))

    def new_project(self, creatorid: str, active_config: str):
    
        """Inserts new project into database
        :param creatorid: Identifier of project creator
        :param active_config: Identifier of currently active project configuration                
        :param result: Identifier of a new project
        """     
        project_json = dict()
        project_json["projectid"] = str(uuid.uuid4())
        project_json["creatorid"] = creatorid

        project_json["time"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                      
        if active_config:
            project_json["active_config"] = active_config
        else:
            project_json["active_config"] = ""
            
        project_json["checklist"] = [] 
                              
        if self.connection_problem:
            self.connect_db()
        if self.mycol is not None:
            self.mycol.insert_one(self.parse_json(project_json))
            return  project_json["projectid"]
         
    def load_project(self, projectid: str):
    
        """Shows scan project with given id
        :param projectid: Identifier of a scan project
        :return: JSON object of project
        """
        if self.connection_problem:
            self.connect_db()
            
        if self.mycol is not None:                
            myquery = { "projectid": projectid }
            mydoc = self.mycol.find(myquery)
            for x in mydoc:
                return x

    def set_config(self, projectid: str, configid: str):
    
        """Changes an active configuration of a given scan project
        :param projectid: Identifier of a scan project
        :param configid: Identifier of currently active project configuration that we want to assign     
        :return: JSON object of user
        """

        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:           

            myquery = {"projectid": projectid}
            new_value = {"$set": {"active_config": configid}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))   
    
    def delete_project(self, projectid: str):
    
        """Deletes the project with given id from database
        :param projectid: Identifier of a project which is about to be deleted
        """
        if self.connection_problem:
            self.connect_db()
            
        if self.mycol is not None:          
            myquery = {"projectid": projectid}
            mydoc = self.mycol.delete_one(myquery)

    def all_projects(self) -> str:
    
        """Shows all the scan projects from the database
        :return: String of all database records concatenated
        """
        if self.connection_problem:
            self.connect_db()
            
        if self.mycol is not None:        
            cursor = self.mycol.find({})
            output = ""
            for doc in cursor:
                output = output + str(doc)
            return output

    def all_projects_by_user(self, creatorid: str) -> str:
    
        """Shows all the scan projects from the database created by guven user
        :param creatorid: Identifier of project creator        
        :return: String of all database records concatenated for given user creator
        """
        if self.connection_problem==True:
            self.connect_db()

        if self.mycol is not None:        
            myquery = {"creatorid": creatorid}
            cursor = self.mycol.find(myquery)
            output = ""
            for doc in cursor:
                output = output + str(doc)
            return output

    def add_check(self, projectid: str, check: str):
    
        """Adds a new check to the list of enabled checks for particular project
        :param projectid: Identifier of a scan project
        :param check: Name of the enabled check     
        """
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:           
            current_project = self.load_project(projectid)
            current_list = current_project["checklist"]
            current_list.append(check)
            myquery = { "projectid": projectid }
            new_value = {"$set": { "checklist": current_list }}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))   


    def remove_check(self, projectid: str, check: str):
    
        """Removes the given check from the list of enabled checks for particular project
        :param projectid: Identifier of a scan project
        :param check: Name of the disabled check     
        """
        
        if self.connection_problem:
            self.connect_db()

        if self.mycol is not None:           
            current_project = self.load_project(projectid) 
            current_list = current_project["checklist"]
            current_list.remove(check)
            myquery = {"projectid": projectid}
            new_value = {"$set": { "checklist": current_list}}
            try:
                self.mycol.find_one_and_update(myquery, new_value, upsert=True)
            except Exception as e:
                print(str(e))