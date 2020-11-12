#!/usr/bin/env python
"""
CGNX script to get all operators

tkamath@paloaltonetworks.com

"""
import cloudgenix
import pandas as pd
import os
import sys
import yaml
from netaddr import IPAddress, IPNetwork
from random import *
import argparse
import logging
import datetime


# Global Vars
SDK_VERSION = cloudgenix.version
SCRIPT_NAME = 'CloudGenix: Get Operators'


# Set NON-SYSLOG logging to use function name
logger = logging.getLogger(__name__)

try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # will get caught below.
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None


def go():
    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

    # Allow Controller modification and debug level sets.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. "
                                       "C-Prod: https://api.elcapitan.cloudgenix.com",
                                  default="https://api.elcapitan.cloudgenix.com")

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                             default=None)
    login_group.add_argument("--pass", "-P", help="Use this Password instead of prompting",
                             default=None)

    args = vars(parser.parse_args())

    ############################################################################
    # Instantiate API & Login
    ############################################################################

    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=False)
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, SDK_VERSION, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]
    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None

    ############################################################################
    # Get Operators
    ############################################################################
    roles_id_name = {}
    resp = cgx_session.get.roles()
    if resp.cgx_status:
        rolelist = resp.cgx_content.get("items", None)
        for role in rolelist:
            roles_id_name[role['id']] = role['name']

    else:
        print("ERR: Could not retrieve roles")
        cloudgenix.jd_detailed(resp)


    userlist = pd.DataFrame()
    print("INFO: Retrieving operators")
    resp = cgx_session.get.tenant_operators()

    if resp.cgx_status:
        operators = resp.cgx_content.get("items", None)

        for op in operators:
            first_name = ""
            last_name = ""
            email = ""
            rolestr = ""
            crolestr = ""
            if "first_name" in op.keys():
                first_name = op.get("first_name", None)

            if "last_name" in op.keys():
                last_name = op.get("last_name", None)

            if "email" in op.keys():
                email = op.get("email", None)

            if "roles" in op.keys():
                roles = op.get("roles", None)
                for role in roles:
                    rolestr = rolestr + "{},".format(role['name'])

            if "custom_roles" in op.keys():
                customroles = op.get("custom_roles", None)

                for crole in customroles:
                    cid = crole['id']
                    if cid in roles_id_name.keys():
                        cname = roles_id_name[cid]
                    else:
                        cname = cid

                    crolestr = crolestr + "{},".format(cname)

            userlist = userlist.append({"First Name": first_name,
                                        "Last Name": last_name,
                                        "Email": email,
                                        "Roles": rolestr[:-1],
                                        "Custom Roles": crolestr[:-1]}, ignore_index=True)

        ############################################################################
        # Store file
        ############################################################################
        curtime_str = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        filename = "{}/operators_{}.csv".format(os.getcwd(), curtime_str)
        print("INFO: Operators retrieved.. Saving to file {}".format(filename))

        userlist.to_csv(filename,index=False)


    else:
        print("ERR: Could not query operators")
        cloudgenix.jd_detailed(resp)

    ############################################################################
    # Logout to clear session.
    ############################################################################
    cgx_session.get.logout()

    print("INFO: Logging Out")
    sys.exit()

if __name__ == "__main__":
    go()
