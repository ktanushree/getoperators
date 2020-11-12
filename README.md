# CloudGenix Get Operators 
This script is used to query all the operators configured on the CloudFenix AppFabric and download it into a CSV.

#### Synopsis
This script is used to download all the operators configured on the CloudGenix AppFabric

#### Requirements
* Active CloudGenix Account
* Python >= 2.7 or >=3.6
* Python modules:
    * CloudGenix Python SDK >= 5.4.3b1 - <https://github.com/CloudGenix/sdk-python>

#### License
MIT

#### Installation:
 - **Github:** Download files to a local directory, manually run `getoperators.py`. 

#### Usage:
Download all operators into a CSV file:
```
./getoperators.py 
```

#### Help Text:
```
usage: getoperators.py [-h] [--controller CONTROLLER] [--email EMAIL]
                       [--pass PASS]

CloudGenix: Get Operators.

optional arguments:
  -h, --help            show this help message and exit

API:
  These options change how this program connects to the API.

  --controller CONTROLLER, -C CONTROLLER
                        Controller URI, ex. C-Prod:
                        https://api.elcapitan.cloudgenix.com

Login:
  These options allow skipping of interactive login

  --email EMAIL, -E EMAIL
                        Use this email as User Name instead of prompting
  --pass PASS, -P PASS  Use this Password instead of prompting
```

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional CloudGenix Documentation at <http://support.cloudgenix.com>
