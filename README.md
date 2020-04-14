# connectwise_manage

## Introduction
This script synchronizes resources from LogicMonitor into ConnectWise Manage CMDB. It can be used as the script for a Python based datasource in LogicMonitor so that it runs on a regular schedule and reports back the count of devices in each state. This also allows for thresholding/alarming.

## Installation

To install this package, run the following at your command line:

```
git clone https://github.com/ianbloom/connectwise_manage.git
```

Then, run the following:

```
sudo python setup.py install
```

## Setup

Synchronizes devices from LM to CW Manage CMDB and reports on the number of devices in each state: failed to synchronize, synchronized new, synchronized existing. Synchronization uses display name as the unique ID. Changing the display name in LM will result in an orphan in CW and a newly created CI.

API creds req'd as properties on resource [portal].logicmonitor.com or a collector:
- lm2cw.cw_agentid.pass=agentid from CW through dev portal. This IDs the integration itself.
- lm2cw.cw_company=CW company
- lm2cw.cw_private.pass=CW private key
- lm2cw.cw_public=CW public key
- lm2cw.cw_site=instance hosting site FQDN (staging.connectwisedev.com)
- lm2cw.lm_company=LM portal name. For acme.logicmonitor.com: "acme"
- lm2cw.lm_id=API Token Access ID
- lm2cw.lm_key.pass=API Token Access Key

Each device to be synchronized into CW requires a companyid property which is the numeric id of the company to which the device belongs in CW. That property name is "cw_company".  It must also have a valid type, i.e. the type must exist in CW. The type is specified by the property "cw_type". This property can be specified on a device level or as a group level property, inherited by all children of the group.

**Type lookups are performed by name, and users must be certain to match fields between CW and LM precisely**

## Usage

For information about the required variables, run the following:

```
python connectwise_scrape.py -h
```

## Example

For my LogicMonitor account, I run the following:

```
python3 connectwise_scrape.py --info --cw_agentid XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX --cw_company logicmonitor_c --cw_private XXXXXXXXXXXXXXXX --cw_public XXXXXXXXXXXXXXXX --cw_site staging.connectwisedev.com --lm_company lmstuartweenig --lm_id XXXXXXXXXXXXXXXXXXXX --lm_key "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

If you'd like to schedule a recurring job to run the synchronization, make use of Linux's [crontab](http://www.adminschoice.com/crontab-quick-reference) or Windows' [Task Scheduler](https://docs.microsoft.com/en-us/windows/desktop/taskschd/task-scheduler-start-page).

## Result

The result will be a ConnectWise configuration entry for each device in LogicMonitor.

![Optional Text](https://github.com/ianbloom/connectwise_manage/blob/master/images/Screen%20Shot%202018-09-20%20at%2010.59.15%20AM.png)
