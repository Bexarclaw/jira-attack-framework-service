#!/usr/bin/env python3
"""
JIRA Attack Framework Service (JAFRS)
Automates MITRE ATT&CK coverage tracking in Jira Software Cloud

Rebranded from: attack2jira
Original Authors: Mauricio Velazco, Olindo Verrillo
License: BSD 3-Clause
"""

from attackcti import attack_client
import json, sys, argparse, traceback
from getpass import getpass
from lib.jirahandler import JiraHandler
from argparse import RawTextHelpFormatter


class JiraAttackFrameworkService:
    """
    Main orchestrator for JIRA Attack Framework Service.
    Manages MITRE ATT&CK technique synchronization with Jira.
    """

    jirahandler = None

    def __init__(self, url, username, password):
        """
        Initialize JAFRS with Jira credentials.

        Args:
            url (str): Jira Cloud instance URL
            username (str): Jira user email
            password (str): Jira API token
        """
        jirahandler = JiraHandler(url, username, password)
        self.jirahandler = jirahandler

    def get_attack_techniques(self):
        """
        Fetch all enterprise techniques from MITRE ATT&CK.

        DEPRECATED: Kept for backward compatibility.
        Use create_attack_techniques_and_subtechniques() instead.

        Returns:
            list: List of technique dictionaries or None on error
        """
        try:
            print("[*] Obtaining ATT&CK's techniques...")
            client = attack_client()
            all_enterprise = client.get_enterprise()
            techniques = []
            for technique in all_enterprise['techniques']:
                tech = json.loads(technique.serialize())
                # avoid bringing in the revoked techniques
                if not 'revoked' in tech.keys():
                    techniques.append(tech)
            print("[!] Done!")
            return techniques

        except:
            traceback.print_exc(file=sys.stdout)
            print("[!] Error connecting to Att&ck's API !")
            return

    def create_attack_techniques(self, key):
        """
        Create flat technique list in Jira.

        DEPRECATED: Use create_attack_techniques_and_subtechniques() instead.

        Args:
            key (str): Jira project key
        """
        techniques = self.get_attack_techniques()
        jiraclient = self.jirahandler

        print("[*] Creating Jira issues for ATT&CK's techniques...")
        for technique in techniques:
            try:

                custom_fields = self.jirahandler.get_custom_fields()

                name = technique['name']
                id = technique['external_references'][0]['external_id']
                url = technique['external_references'][0]['url']
                tactic = technique['kill_chain_phases'][0]['phase_name']
                description = technique['description']

                # some techniques dont have the field populated
                if 'x_mitre_data_sources' in technique.keys():
                    datasources = technique['x_mitre_data_sources']
                else:
                    datasources = []

                ds_payload = []
                for ds in datasources:
                    ds_payload.append({'value': ds.title()})

                issue_dict = {
                    "fields": {
                        "project": {"key": key},
                        "summary": name + " (" + id + ")",
                        "description": description,
                        "issuetype": {"name": "Task"},
                        custom_fields['id']: id,
                        custom_fields['tactic']: {'value': tactic},
                        custom_fields['maturity']: {'value': 'Not Tracked'},
                        custom_fields['url']: url,
                        custom_fields['datasources']: ds_payload,
                    }
                }
                jiraclient.create_issue(issue_dict, id)

            except Exception as ex:
                print("\t[*] Could not create ticket for " + id)
                print(ex)
                traceback.print_exc(file=sys.stdout)
                pass

        print("[*] Done!")

    def create_attack_techniques_and_subtechniques(self, key):
        """
        Create hierarchical technique structure with sub-techniques.

        Parent techniques are created as Tasks, sub-techniques as Sub-tasks.

        Args:
            key (str): Jira project key
        """
        jiraclient = self.jirahandler
        techniques = self.get_attack_techniques()
        sorted_techniques = sorted(techniques, key=lambda k: k['external_references'][0]['external_id'])

        print("[*] Creating Jira issues for ATT&CK's techniques...")

        for technique in sorted_techniques:
            try:
                custom_fields = self.jirahandler.get_custom_fields()

                name = technique['name']
                id = technique['external_references'][0]['external_id']
                url = technique['external_references'][0]['url']
                tactic = technique['kill_chain_phases'][0]['phase_name']
                description = technique['description']

                # some techniques dont have the field populated
                if 'x_mitre_data_sources' in technique.keys():
                    datasources = technique['x_mitre_data_sources']
                else:
                    datasources = []

                ds_payload = []
                for ds in datasources:
                    ds_payload.append({'value': ds.title()})

                if not technique['x_mitre_is_subtechnique']:
                    # Not a sub-technique
                    issue_dict = {
                        "fields": {
                            "project": {"key": key},
                            "summary": name,
                            "description": description,
                            "issuetype": {"name": "Task"},
                            custom_fields['Id']: id,
                            custom_fields['Tactic']: {'value': tactic},
                            custom_fields['Maturity']: {'value': 'Not Tracked'},
                            custom_fields['Url']: url,
                            custom_fields['Datasources']: ds_payload,
                        }
                    }
                    parent_id = jiraclient.create_issue(issue_dict, id)

                else:
                    # Sub-technique
                    issue_dict = {
                        "fields": {
                            "parent": {"id": parent_id['id']},
                            "project": {"key": key},
                            "summary": name,
                            "description": description,
                            "issuetype": {"name": "Sub-task"},
                            custom_fields['Id']: id,
                            custom_fields['Tactic']: {'value': tactic},
                            custom_fields['Maturity']: {'value': 'Not Tracked'},
                            custom_fields['Url']: url,
                            custom_fields['Datasources']: ds_payload,
                            custom_fields['Sub-Technique of']: jiraclient.url + "/browse/" + parent_id['key'],
                        }
                    }
                    ret_id = jiraclient.create_issue(issue_dict, id)

            except Exception as ex:
                print("\t[*] Could not create ticket for " + id)
                print(ex)
                traceback.print_exc(file=sys.stdout)
                pass

        print("[*] Done!")

    def generate_json_layer(self, hideDisabled):
        """
        Generate ATT&CK Navigator JSON layer based on Jira maturity levels.

        Args:
            hideDisabled (bool): If True, hides "Not Tracked" techniques
        """
        VERSION = "2.2"
        NAME = "JIRA Attack Framework Service"
        DESCRIPTION = "ATT&CK Coverage exported from JAFRS"
        DOMAIN = "mitre-enterprise"
        GRADIENT = {
            "colors": [
                "#DCDCDC",
                "#03ad03"],
        }

        layer_json = {
            "domain": DOMAIN,
            "name": NAME,
            "description": DESCRIPTION,
            "gradient": GRADIENT,
            "version": VERSION,
            "hideDisabled": hideDisabled,
            "techniques": []
        }

        # Define your colors here
        not_tracked_color = "#DCDCDC"
        shade_0_color = "#e1fce1"  # lightest green
        shade_1_color = "#81fc81"  # lighter green
        shade_2_color = "#49fc49"  # green
        shade_3_color = "#03ad03"  # darker green

        res_dict = self.jirahandler.get_technique_maturity()
        for key in res_dict.keys():
            enabled = True
            if res_dict[key]['value'] == "Not Tracked":
                enabled = False
                color = not_tracked_color
            elif res_dict[key]['value'] == "Initial":
                color = shade_0_color
            elif res_dict[key]['value'] == "Defined":
                color = shade_1_color
            elif res_dict[key]['value'] == "Resilient":
                color = shade_2_color
            elif res_dict[key]['value'] == "Optimized":
                color = shade_3_color

            technique = {
                "techniqueID": key,
                "enabled": enabled,
                "color": color
            }
            layer_json["techniques"].append(technique)

        print("[*] Outputting JSON layer coverage_layer.json")
        with open('coverage_layer.json', 'w', encoding='utf-8') as f:
            json.dump(layer_json, f, ensure_ascii=False, indent=4)

    def set_up_jira_automated(self, project, key):
        """
        Complete automated Jira setup workflow.

        Args:
            project (str): Jira project display name
            key (str): Jira project key
        """
        self.jirahandler.create_project(project, key)
        self.jirahandler.create_custom_fields()
        self.jirahandler.add_custom_field_options()
        self.jirahandler.add_custom_fields_to_screen(key)
        self.jirahandler.hide_unwanted_fields(key)
        self.create_attack_techniques_and_subtechniques(key)


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(
        description='JIRA Attack Framework Service - Automate MITRE ATT&CK coverage tracking in Jira',
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('-url', dest='url', type=str, help='Url of Jira instance', default="")
    parser.add_argument('-u', dest='user', type=str, help='Username', default="")
    parser.add_argument('-a', dest='action', type=str, default="",
                        help='action to execute\nTwo supported:\n\'initialize\' will create the JIRA entities. \n\'export\' will export the JSON layer.')
    parser.add_argument('-p', dest='project', type=str, help='Name of the Jira project to create.',
                        default="Mitre Attack Framework")
    parser.add_argument('-k', dest='key', type=str, help='Project Key.(default=\'ATTACK\')', default="ATTACK")
    parser.add_argument('-hide', help='If set, \'Not Tracked\' techniques will be hidden', action='store_true')
    results = parser.parse_args()

    url = results.url
    user = results.user
    action = results.action
    hideDisabled = results.hide
    project = results.project
    key = results.key

    if (url and user and action):
        pswd = getpass('Jira API Token for ' + user + ":")

        if (action == "initialize"):
            jafrs = JiraAttackFrameworkService(url, user, pswd)
            jafrs.set_up_jira_automated(project, key)

        if (action == "export"):
            jafrs = JiraAttackFrameworkService(url, user, pswd)
            jafrs.generate_json_layer(hideDisabled)
    else:
        parser.print_help()


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print("\n")
        print("[!] Exiting JIRA Attack Framework Service")
        sys.exit()
