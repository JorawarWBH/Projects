"""
This file will have jiraWebApi class.

This module will also have jql support in which
user get can specific people issues.

This module will have different class such board and userissue

"""

from config import __jira_credentials__
from jira.client import JIRA
from jira.exceptions import *
from miscellaneous.miscellaneousFunctions import multi_getattr,castToInt

from miscellaneous.miscellaneousFunctions import rawJsonconvertorFromList, rawJsonCovertorFromDict
import datetime
import time


def to_datetime(timestamp):
    """ Converts timestamp (str) in datetime object. """
    return datetime.datetime(*time.strptime(timestamp[:19], '%Y-%m-%dT%H:%M:%S')[:6])

class jiraBoard():
    """This class will have issue related to an project"""

    def __init__(self, client, jiraBoardObj):
        self.client = client
        self.jiraBoardObj = jiraBoardObj
        self.boardId = multi_getattr(self.jiraBoardObj, "id")
        self.boardName = multi_getattr(self.jiraBoardObj, "name")

    def boardInformation(self):
        response = {}
        response["board_id"] = self.boardId
        response["board_name"] = self.boardName
        response["filter_id"] = multi_getattr(self.jiraBoardObj, "filter.id")
        response["filter_name"] = multi_getattr(self.jiraBoardObj, "filter.name")
        response["filter_query"] = multi_getattr(self.jiraBoardObj, "filter.query")
        response["filter_owner_user_name"] = multi_getattr(self.jiraBoardObj, "filter.owner.userName")
        response["filter_owner_display_name"] = multi_getattr(self.jiraBoardObj, "filter.owner.displayName")
        response["projects"] = [{"projectId": x.id, "projectName": x.name, "projectKey": x.key} for x in
                                multi_getattr(self.jiraBoardObj, "filter.queryProjects.projects")]
        response["board_admins"] = self.jiraBoardObj.raw["boardAdmins"]
        response["location_display_text"] = multi_getattr(self.jiraBoardObj, "location.displayText")
        response["location_type"] = multi_getattr(self.jiraBoardObj, "location.type")
        response["location_key"] = multi_getattr(self.jiraBoardObj, "location.locationKey")
        return response

    def jiraColumns(self):
        """This method return all the in which an issue can be place such to do or done etc"""
        payLoad = self.client.statuses()
        response = []
        for obj in payLoad:
            singleDict = {}
            singleDict.update({"board_id": self.boardId})
            singleDict.update({"board_name": self.boardName})
            singleDict.update({"column_description": multi_getattr(obj, "description")})
            singleDict.update({"column_name": multi_getattr(obj, "name")})
            singleDict.update({"column_id": int(multi_getattr(obj, "id"))})
            singleDict.update({"column_status_category_id": int(multi_getattr(obj, "statusCategory.id"))})
            singleDict.update({"column_status_category_key": multi_getattr(obj, "statusCategory.key")})
            singleDict.update({"column_status_category_color_name": multi_getattr(obj, "statusCategory.colorName")})
            response.append(singleDict)
        return response

    def sprints(self):
        payLoad = self.client.sprints(board_id=self.boardId,extended=True)
        sprintIds = [x.id for x in payLoad]
        data = []
        for stringId in sprintIds:
            singleDict = {}
            sprintInfoObj = self.client.sprint_info(board_id=self.boardId, sprint_id=stringId)
            singleDict.update({"board_id": self.boardId})
            singleDict.update({"sprint_id": sprintInfoObj.get("id")})
            singleDict.update({"sprint_name": sprintInfoObj.get("name")})
            singleDict.update({"state": sprintInfoObj.get("state")})
            singleDict.update({"goal": sprintInfoObj.get("goal")})
            singleDict.update({"start_date": sprintInfoObj.get("startDate")})
            singleDict.update({"end_date": sprintInfoObj.get("endDate")})
            singleDict.update({"iso_start_date": sprintInfoObj.get("isoStartDate")})
            singleDict.update({"iso_end_date": sprintInfoObj.get("isoEndDate")})
            singleDict.update({"complete_date": sprintInfoObj.get("completeDate")})
            singleDict.update({"iso_complete_date": sprintInfoObj.get("isoCompleteDate")})
            singleDict.update({"can_update_sprint": sprintInfoObj.get("canUpdateSprint")})
            singleDict.update({"days_remaining": sprintInfoObj.get("daysRemaining")})
            data.append(singleDict)
        response = {"data": data, "totalNumberOfSprint": len(data)}
        return response


class project():
    def __init__(self, client, projectId):
        self.client = client
        self.projectObj = self.client.project(id=projectId)
        self.projectKey = multi_getattr(self.projectObj, "key")
        self.projectId = castToInt(multi_getattr(self.projectObj, "id"))
        self.projectLeadAccountId = multi_getattr(self.projectObj, "lead.accountId")

    def projectInformation(self):
        response = {}
        response["project_id"] = self.projectId
        response["project_key"] = self.projectObj.key
        response["project_description"] = self.projectObj.description
        response["project_lead_account_id"] = multi_getattr(self.projectObj, "lead.accountId")

        response["project_lead"] = {"key": multi_getattr(self.projectObj, "lead.key"),
                                   "accountId": multi_getattr(self.projectObj, "lead.accountId"),
                                   "displayName": multi_getattr(self.projectObj, "lead.displayName"),
                                   "active": multi_getattr(self.projectObj, "lead.active")}
        response["project_issue_types"] = [{"name": obj.name, "id": obj.id} for obj in
                                         multi_getattr(self.projectObj, "issueTypes", [])]
        response["project_assignee_type"] = multi_getattr(self.projectObj, "assigneeType")
        response["project_name"] = multi_getattr(self.projectObj, "name")
        response["project_roles"] = self.projectObj.raw["roles"]
        response["project_type_key"] = multi_getattr(self.projectObj, "projectTypeKey")
        response["project_is_private"] = multi_getattr(self.projectObj, "isPrivate")
        response["project_properties"] = self.projectObj.raw["properties"]
        response["assigned_boards_name"] = [obj.name for obj in self.m_assignedBoards()]
        response["assigned_boards_id"] = [obj.id for obj in self.m_assignedBoards()]
        return response

    def projectIssueTypes(self):
        response = {}
        response["data"]= [{"project_id":castToInt(self.projectId),"issue_type_name": obj.name, "issue_type_id": castToInt(obj.id)} for obj in
                                         multi_getattr(self.projectObj, "issueTypes", [])]
        return response

    def projectMembers(self):
        "Here username='' meaning match any member for this  project "
        payLoad = self.client.search_assignable_users_for_projects(username="", projectKeys=self.projectKey)
        memberList = []
        for obj in payLoad:
            singleDict = {}
            singleDict.update({"project_id": self.projectId})
            singleDict.update({"project_key": self.projectKey})
            singleDict.update({"member_key": multi_getattr(obj, "key")})
            singleDict.update({"member_account_id": multi_getattr(obj, "accountId")})
            singleDict.update({"member_account_type": multi_getattr(obj, "accountType")})
            singleDict.update({"member_name": multi_getattr(obj, "name")})
            singleDict.update({"member_email_address": multi_getattr(obj, "emailAddress")})
            singleDict.update({"member_display_name": multi_getattr(obj, "displayName")})
            singleDict.update({"member_active": multi_getattr(obj, "active")})
            singleDict.update({"member_time_zone": multi_getattr(obj, "timeZone")})
            singleDict.update({"member_locale": multi_getattr(obj, "locale")})
            memberList.append(singleDict)
        response = {"data": memberList, "totalMembers": len(memberList)}
        return response

    def m_assignedBoards(self):

        boardsObjList = []
        for obj in self.client.boards():
            for projectDoc in obj.filter.queryProjects.projects:
                if projectDoc.id == self.projectId:
                    boardsObjList.append(obj)
        return boardsObjList


    def m_assignedBoards(self):

        boardsObjList = []
        for obj in self.client.boards():
            for projectDoc in obj.filter.queryProjects.projects:
                if projectDoc.id == self.projectId:
                    boardsObjList.append(obj)
        return boardsObjList





class issue():
    """we have to make proper function of which proivde instend of creating classs variable.
    i swear i will not stop updating this project."""

    def __init__(self, client, issueId):
        self.client = client
        self.issueObj = client.issue(issueId)
        self.issueId = self.issueObj.id
        self.issueKey = self.issueObj.key
        self.issueTypeName = multi_getattr(self.issueObj, "fields.issuetype.name")
        self.issueParentId = multi_getattr(self.issueObj, "fields.parent.id")
        self.issueProjectId = multi_getattr(self.issueObj, "fields.project.id")

    def issueInformation(self):

        response = {}
        response["issue_id"] = castToInt(multi_getattr(self.issueObj, "id"))
        response["issue_key"] = multi_getattr(self.issueObj, "key")
        response["issue_type_name"] = multi_getattr(self.issueObj, "fields.issuetype.name")
        response["issue_type_id"] = castToInt(multi_getattr(self.issueObj, "fields.issuetype.id"))
        response["issue_type_description"] = multi_getattr(self.issueObj, "fields.issuetype.description")
        response["is_sub_task"] = multi_getattr(self.issueObj, "fields.issuetype.subtask")
        response["issue_parent_id"] = castToInt(multi_getattr(self.issueObj, "fields.parent.id"))
        response["issue_project_id"] = multi_getattr(self.issueObj, "fields.project.id")
        response["issue_parent_id"] = multi_getattr(self.issueObj, "fields.parent.id")
        response["issue_parent_key"] = multi_getattr(self.issueObj, "fields.parent.key")
        response["time_spent_seconds"] = multi_getattr(self.issueObj, "fields.timespent")
      #  response["issue_project_id"] = multi_getattr(self.issueObj, "fields.project.id")
        response["issue_project_key"] = multi_getattr(self.issueObj, "fields.project.key")
        response["issue_project_name"] = multi_getattr(self.issueObj, "fields.project.name")
        response["resolution"] = self.m_resolution()
        response["created_date"] = multi_getattr(self.issueObj, "fields.created")
        response["priority_id"] = castToInt(multi_getattr(self.issueObj, "fields.priority.id"))
        response["priority_name"] = multi_getattr(self.issueObj, "fields.priority.name")
        response["assignee_account_id"] = multi_getattr(self.issueObj, "fields.assignee.accountId")
        response["assignee_json"] = self.m_assignee()
        response["updated_date"] = multi_getattr(self.issueObj, "fields.updated")
        response["status_name"] = multi_getattr(self.issueObj, "fields.status.name")
        response["status_id"] = castToInt(multi_getattr(self.issueObj, "fields.status.id"))
        #         response["comments"]            = self.comments()
        response["due_date"] = multi_getattr(self.issueObj, "fields.duedate")
        response["progress_time_spend"] = castToInt(multi_getattr(self.issueObj, "fields.progress.progress"))
        response["total_given_time"] = castToInt(multi_getattr(self.issueObj, "fields.progress.total"))
        response["progress_percent"] = castToInt(multi_getattr(self.issueObj, "fields.progress.percent"))
        response["reporter_account_id"] = multi_getattr(self.issueObj, "fields.reporter.accountId")
        response["reporter_json"] = self.m_reporter()
        response["creator_account_id"] = multi_getattr(self.issueObj, "fields.creator.accountId")
        response["creator_json"] = self.m_creator()

        return response

    def issueHistory(self):
        payload = self.client.search_issues("id={}".format(self.issueId), expand='changelog')[0]
        # print(payload)
        response = []
        for doc in payload.raw["changelog"]["histories"]:
            # print("******************")
            del doc["author"]["avatarUrls"]
            mapping={
                "field":"field",
                "fieldtype": "field_type",
                "fieldId": "field_id",
                "from": "event_from_id",
                "fromString": "event_from_string",
                "to": "event_to_id",
                "toString": "event_to_string",
                "author": "author",
                "created": "created",
            }
            for item_list in doc["items"]:
                singleDict = {}
                fields = ["field", "fieldtype", "fieldId", "from", "fromString", "to", "toString"]
                for field in fields:
                    to_field=mapping[field]
                    try:
                            singleDict[to_field] = item_list[field]
                    except KeyError:
                        singleDict[to_field] = None
                singleDict["author"] = doc["author"]
                singleDict["created"] = doc["created"]
                singleDict["issue_id"] = int(self.issueId)
                response.append(singleDict)
        return response

    def m_resolution(self):
        """
        It return status such as "To DO" or "DONE" ...etc
        :return:
            name
            id
            description
            date
        """
        issueResolutionId = multi_getattr(self.issueObj, "fields.resolution.id", None)
        issueResolutionName = multi_getattr(self.issueObj, "fields.resolution.name", None)
        issueDescription = multi_getattr(self.issueObj, "fields.resolution.description", None)
        resolutionDate = multi_getattr(self.issueObj, "fields.resolutiondate", None)
        return {"name": issueResolutionName, "id": issueResolutionId, "description": issueDescription,
                "date": resolutionDate}

    def m_assignee(self):
        """
        its provide the details about person whom this issue appointed


        :return:
            name
            key
            accountID
            emailAddress
            displayName
            isActive
        """

        name = multi_getattr(self.issueObj, "fields.assignee.name", None)
        key = multi_getattr(self.issueObj, "fields.assignee.key", None)
        accountId = multi_getattr(self.issueObj, "fields.assignee.accountId", None)
        emailAddress = multi_getattr(self.issueObj, "fields.assignee.emailAddress", None)
        displayName = multi_getattr(self.issueObj, "fields.assignee.displayName", None)
        isActive = multi_getattr(self.issueObj, "fields.assignee.active", None)
        return {"name": name, "key": key, "accountId": accountId, "emailAddress": emailAddress,
                "displayName": displayName,
                "isActive": isActive}

    def comments(self):
        """

        :return:
            authorDisplayName
            authorName
            authorAccountId
            authorComment
            dateCreated
            dateUpdated
        """
        preprocessed_dict = []
        for singleComment in multi_getattr(self.issueObj, "fields.comment.comments", []):
            displayName = multi_getattr(singleComment, "author.displayName")
            name = multi_getattr(singleComment, "author.name")
            accountId = multi_getattr(singleComment, "author.accountId")
            comment = multi_getattr(singleComment.body.content[0].content[0],"text")

            created = multi_getattr(singleComment, "created")
            updated = multi_getattr(singleComment, "updated")
            preprocessed_dict.append({"issue_id": int(self.issueId), "author_display_name": displayName, "author_name": name,
                                      "author_account_id": accountId, "author_comment": comment,
                                      "date_created": created, "date_updated": updated})
        return {"data": preprocessed_dict, "totalComment": self.issueObj.fields.comment.total}

    def m_reporter(self):
        """
        To whom to report
        :return:
            name
            key
            accountId
            emailAddress
            displayName
            isActive
        """
        name = multi_getattr(self.issueObj, "fields.reporter.name")
        key = multi_getattr(self.issueObj, "fields.reporter.key")
        accountId = multi_getattr(self.issueObj, "fields.reporter.accountId")
        emailAddress = multi_getattr(self.issueObj, "fields.reporter.emailAddress")
        displayName = multi_getattr(self.issueObj, "fields.reporter.displayName")
        isActive = multi_getattr(self.issueObj, "fields.reporter.active")
        return {"name": name, "key": key, "accountId": accountId, "emailAddress": emailAddress,
                "displayName": displayName,
                "isActive": isActive}

    def m_creator(self):
        name = multi_getattr(self.issueObj, "fields.creator.name")
        accountId = multi_getattr(self.issueObj, "fields.creator.accountId")
        emailAddress = multi_getattr(self.issueObj, "fields.creator.emailAddress")
        displayName = multi_getattr(self.issueObj, "fields.creator.displayName")
        isActive = multi_getattr(self.issueObj, "fields.creator.active")
        return {"name": name, "accountId": accountId, "emailAddress": emailAddress, "displayName": displayName,
                "isActive": isActive}

    #     def timeTracking(self):
    #         remainingEstimate = self.issueObj.fields.timetracking.remainingEstimate
    #         timeSpenttimeSpent = self.issueObj.fields.timetracking.timeSpent
    #         remainingEstimateSeconds = self.issueObj.fields.timetracking.remainingEstimateSeconds
    #         timeSpentSeconds = self.issueObj.fields.timetracking.timeSpentSeconds
    #         return {"remainingEstimate":remainingEstimate,"timeSpenttimeSpent":timeSpenttimeSpent,
    #                 "remainingEstimateSeconds":remainingEstimateSeconds,"timeSpentSeconds":timeSpentSeconds}

    def lastviewed(self):
        pass

    def votes(self):
        pass

    def workLogs(self):
        pass


class jiraDashBoard():
    """This class will have multi projects reports on issues """
    pass


class user():
    """This class will have every activity did by an user such as- comment ,issues assigneed, name, roles etc"""
    def __init__(self,client):
        self.client=client

    def allUser(self):
        payLoad = self.client.search_users("")
        response = []
        for obj in payLoad:
            singleDict = {}
            singleDict.update({"user_key": multi_getattr(obj, "key")})
            singleDict.update({"user_account_id": multi_getattr(obj, "accountId")})
            singleDict.update({"user_account_type": multi_getattr(obj, "accountType")})
            singleDict.update({"user_name": multi_getattr(obj, "name")})
            singleDict.update({"user_email_address": multi_getattr(obj, "emailAddress")})
            singleDict.update({"user_display_name": multi_getattr(obj, "displayName")})
            singleDict.update({"is_user_active": multi_getattr(obj, "active")})
            singleDict.update({"user_timezone": multi_getattr(obj, "timeZone")})
            singleDict.update({"user_locale": multi_getattr(obj, "locale")})
            response.append(singleDict)
        return response


