- ### maxcontacts

  Manage your Maxima contacts. List, refresh, add, remove or search contacts.

| Parameters | Description |
| :---- | :---- |
| action | action:list, add, remove, search |
| contact | (Optional) The Maxima contact address of another node. Can be found using the "maxima" command. |
| id | (Optional) The id of an existing contact to remove or search for. |
| publickey | (Optional) The Maxima public key of an existing contact to remove or search for. |

- Parameters used with the action: parameter:

| Parameters | Description |
| :---- | :---- |
| list | List your existing webhooks. |
| add | Add a new contact. |
| remove | Remove an existing contact. |
| search | Search for a contact. |

- Examples:  
- Terminal  
- maxcontacts  
- Terminal  
- maxcontacts action:list  
- Terminal  
- maxcontacts action:add contact:MxG18H..  
- Terminal  
- maxcontacts action:remove id:1  
- Terminal  
- maxcontacts action:search publickey:0x3081..  
- maxcreate

Create a 128 bit RSA public and private key.  
You can use them with maxsign and maxverify.  
Terminal  
maxcreate

- ### maxextra

  Perform extra functions on Maxima.

| Parameters | Description |
| :---- | :---- |
| action | action:staticmls, addpermanent, removepermanent, listpermanent, clearpermanent, getaddress, mlsinfo, allowallcontacts, addallowed, listallowed, clearallowed |
| publickey | (Optional) The Maxima public key of the user who wants to share their permanent maxaddress to be publicly contactable over Maxima. |
| maxaddress | (Optional) The Maxima maxaddress of the user who wants to share their permanent maxaddress to be publicly contactable over Maxima. |
| enable | (Optional) true or false, use with action:allowallcontacts to enable or disable all new contacts. |
| host | (Optional) The p2pidentity of a server node which is always online. |

- Parameters used with the action: parameter:

| Parameters | Description |
| :---- | :---- |
| staticmls | Set an unchanging Maxima Location Service (mls) host for yourself. |
| addpermanent | On your static mls node, add your Maxima public key to allow \`getaddress\` requests from anyone. |
| removepermanent | On your static mls node, remove your Maxima public key to stop allowing \`getaddress\` requests. |
| listpermanent | On your static mls node, list all public keys currently allowing public requests for their contact address. |
| clearpermanent | On your static mls node, remove ALL public keys currently allowing requests for their contact address. |
| getaddress | Request the current contact address of a permanently accessible user from their static mls host. |
| mlsinfo | List info about users using you as their mls and the public keys of their contacts. |
| allowallcontacts | If you have shared your permanent maxaddress, you can disable/enable users adding you as a contact. |
| addallowed | If \`allowallcontacts\` is disabled, you can authorize specific users to add you as a contact. Stored in RAM. |
| listallowed | List all the public keys which are allowed to add you as a Maxima contact. |
| clearallowed | Remove the public keys of ALL users which are allowed to add you as a Maxima contact. |

- Examples:  
- Terminal  
- maxextra action:staticmls host:Mx...@34.190.784.3:9001  
- Terminal  
- maxextra action:staticmls host:clear  
- Terminal  
- maxextra action:addpermanent publickey:0x3081..  
- Terminal  
- maxextra action:removepermanent publickey:0x3081..  
- Terminal  
- maxextra action:listpermanent  
- Terminal  
- maxextra action:clearpermanent  
- Terminal  
- maxextra action:getaddress maxaddress:MAX\#0x3081..\#Mx..@34.190.784.3:9001  
- Terminal  
- maxextra action:mlsinfo  
- Terminal  
- maxextra action:allowallcontacts enable:false  
- Terminal  
- maxextra action:addallowed publickey:0x2451..  
- Terminal  
- maxextra action:listallowed  
- Terminal  
- maxextra action:clearallowed

- ### maxima

Check your Maxima details, send a message/data.

| Parameters | Description |
| :---- | :---- |
| action | action:info, setname, hosts, send, sendall, refresh |
| name | (Optional) The name of the user. |
| id | (Optional) The id of the user. |
| to | (Optional) The to of the user. |
| publickey | (Optional) The public key of the user. |
| application | (Optional) The application of the user. |
| data | (Optional) The data of the user. |
| poll | (Optional) true or false, true will poll the send action until successful. |
| delay | (Optional) Only used with poll or with sendall. Delay sending the message by this many milliseconds. |

Parameters used with the action: parameter:

| Parameters | Description |
| :---- | :---- |
| info | Show your Maxima details \- name, publickey, staticmls, mls, local identity, and contact address. |
| setname | Set your Maxima name so your contacts recognize you. Default "noname". |
| hosts | List your Maxima hosts and see their Maxima public key, contact address, last seen time, and if you are connected. |
| send | Send a message to a contact. Must specify "id|to|publickey", "application", and "data" parameters. |
| sendall | Send a message to ALL your contacts. Must specify "application" and "data" parameters. |
| refresh | Refresh your contacts by sending them a network message. |

Examples:  
Terminal  
maxima action:info  
Terminal  
maxima action:setname name:myname  
Terminal  
maxima action:hosts  
Terminal  
maxima action:send id:1 application:appname data:0xFED5..  
Terminal  
maxima action:send to:MxG18H.. application:appname data:0xFED5..  
Terminal  
maxima action:send publickey:0xCD34.. application:ip:port data:0xFED5.. poll:true  
Terminal  
maxima action:refresh

- ### maxsign

Sign and verify data with your Maxima ID.  
Returns the signature of the data, signed with your Maxima private key or the specified key.

| Parameters | Description |
| :---- | :---- |
| data | The 0x HEX data to sign. |
| privatekey | (Optional) The 0x HEX data of the private key from maxcreate. Uses your Maxima ID otherwise. |

Examples:  
Terminal  
maxsign data:0xCD34..  
Terminal  
maxsign data:0xCD34.. privatekey:0x3081..

- ### maxverify

Verify data with a Maxima public key. Returns valid true or false.

| Parameters | Description |
| :---- | :---- |
| data | The 0x HEX data to verify the signature for. |
| publickey | The Maxima public key of the signer. |
| signature | The signature of the data. |

Examples:  
Terminal  
maxverify data:0xCD34.. publickey:0xFED5.. signature:0x4827..  
