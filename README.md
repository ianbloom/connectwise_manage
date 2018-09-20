# connectwise_manage

## Introduction
This script that takes several LogicMonitor reports and a keyfile as input, and produces a CSV of their intersection, then updates a text widget with an HTML table generated from this CSV.

## Installation

To install this package, run the following:

```
git clone https://github.com/ianbloom/connectwise_manage.git
```

Then, run the following:

```
sudo python setup.py install
```

Included in this repo is an example key file (key.txt).  Replace the dummy values in this file with values corresponding to your API credentials from both LogicMonitor and Connectwise Manage

## Setup

This script requires the user to apply the 'company' property to devices which will be used to reference a company for the configuration object.  If no company of this name exists in ConnectWise already, a company will be created with this name.  Any device with no 'company' device property will be assigned to an 'Unknown' company because all configurations must have an attached company.

This script also requires the user to reference by id a group whose subgroups correspond to configuration types in Connectwise.  If no configuration type in Connectwise exists, one will be created because all configurations must be assigned a type.  The simplest solution to this problem is to reference LogicMonitor's 'Device by Type' group.

**Lookups are performed by name, and users must be certain to match fields between CW and LM precisely**

## Usage

For information about the required variables, run the following:

```
python connectwise_scrape.py -h
```

This script takes five arguments:
* _-file_ : Path to file containing API credentials
* _-help_ : The ID of a LogicMonitor device group whose subgroups correspond to Connectwise Configuration Types

## Example

For my LogicMonitor account, I run the following:

```
python connectwise_scrape.py -file keyfile.txt -id 70
```

If you'd like to schedule a recurring job to update the text widget, I encourage you to make use of Linux's [crontab](http://www.adminschoice.com/crontab-quick-reference) or Windows' [Task Scheduler](https://docs.microsoft.com/en-us/windows/desktop/taskschd/task-scheduler-start-page).

## Result

The result will be a ConnectWise configuration entry for each device in LogicMonitor.

![Optional Text](https://github.com/ianbloom/connectwise_manage/blob/master/images/Screen%20Shot%202018-09-20%20at%2010.59.15%20AM.png)


