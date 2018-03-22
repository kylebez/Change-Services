# Change-Services

Uses a console-based selection tree to apply the same service properties to the selected set of services.

Begin by entering the name of the server or its ip. Follow the prompts. Select using the number listed in [] and pressing Enter.

When stated, multiple selections can be made by using a hyphenated range (inclusive) e.g. 1-4, and/or delimating by comma e.g 1,2,3,4

The service properties that will be changed are:

* Maximum/minimum number of instances
* Max time a client will wait for an instance
* Max time an idle instance will run
* Max time a client can use an instance
* Low or high isolation

NOTE: recycling period is not a supported changeable attribute with this tool

NOTE: multiple selection is limited to within same folder

