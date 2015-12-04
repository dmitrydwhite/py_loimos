# Command Line Interface for LOIMOS

## Title Bar

## REPL Window

### Command Prompt

```<TEAM NAME>@<LOCATION>}>```

Example:

```SCIENCE@ATLANTA}>```

Team Names are color coded:

* SCIENCE: White
* DISPATCH: Yellow
* MEDICAL: Red
* RESEARCH: Magenta
* OPERATIONS: Blue
* PLANNING: Cyan
* QUARANTINE: Green

Locations are color coded by their disease areas: Red, Blue, Yellow, Gray

The ```}>``` will be colored White

### Commands

* ```collab```
    - Usage: ```collab [<TEAM>]```
    - Output: 
        + If there is no other team here to collaborate with, or if the Team name provided isn't present in the Player's current location:
            ```
            No other teams in <LOCATION> to collaborate with.
            ```
        + If no param is provided and there is more than one team co-located with the Player, a list of teams to collaborate with will be shown:
          ```
          <TEAM NAME>
          <TEAM NAME>
          ```
        + Player must re-enter the command with the param to successfully collaborate.
        + No param is needed if there is only one other team co-located with the Player.
        + If the Player is NOT the **Research Team**:
            * The command will automatically check the Research that both players have, as well as their location, and determine how the Research will transfer.
            * Based on who has the research, both Players will be shown one of the following messages:
              ```
              SUBMIT your Research on <LOCATION> to the <TEAM NAME> Team?(Y/N)
              ACCEPT Research on <LOCATION> from the <TEAM NAME> Team?(Y/N)
              ```
            * Once both teams agree, the Research will be transferred.
            * If neither team has the Research pertaining to their current location:
                ```
                No baseline Data for collaboration here.
                ```
        + If the Player is the **Research Team**:
            ```
            Which Research Data would you like to Submit to <TEAM NAME>?
            1. <CITY NAME>
            2. <CITY NAME>
            3. <CITY NAME>
            4. ACCEPT RESEARCH FROM <TEAM NAME>
            Enter Number:
            ```
        + Once the **Research Team** has selected the number, the same confirmation messages will be displayed to both teams involved in the transaction.
* ```treat```
    - Usage: ```treat <DISEASE>```
    - Output: 
      ```
      submitting treatment plan for <DISEASE>...
      RESULTS: <DISEASE> incidences in <LOCATION> reduced to <NEW DISEASE VALUE>
      ```

* ```cure```
* ```ride```
* ```book```
* ```shuttle```
    - Usage: ```shuttle [<LOCATION>]```
    - Output:
        + If Player is not in a valid shuttle Location (i.e. there is no Research Station here): ```ERROR: No Research Station here to shuttle from```
        + If no param is given or the Location given is not a valid shuttle destination:
          ```
          The following are available SHUTTLE LOCATIONS:
          <CITY NAME>
          <CITY NAME>
          ```
        + Or, if there are no available shuttle destinations in play:
        ```No available SHUTTLE LOCATIONS```
        + If Player has entered a valid Location, then a confirmation message will be shown: ```CONFIRM: SHUTTLE from <CURRENT LOCATION> to <DESTINATION>? (Y/N)```
        + Upon Player confirmation: 
          ```
          SHUTTLE FLIGHT booked to <DESTINATION>.
          Logging out at <CURRENT LOCATION>...
          ...Logging in at <DESTINATION>
          ```
* ```station```
    - Usage: ```station```
    - Output:
        + If Player is able to build a Research Station in their current Location:
        ```Construction contract submitted for RESEARCH STATION in <LOCATION>.  Construction underway.```
        + If Player is NOT able to build a Research Station in their current Location:
        ```Resources are unavailable to build a RESEARCH STATION here.```
* ```review```
    - Usage: ```review```
    - Output: 
        + Shows list of current assets available to the Player
          ```
          1. RESEARCH from <CITY NAME> on <DISEASE>
          2. GRANT for <EVENT>
          ```
        + Example:
          ```
          review
          1. RESEARCH from ATLANTA on CARCINOSIS
          2. RESEARCH from SYDNEY on BALACOGEA
          3. RESEARCH from JAKARTA on BALACOGEA
          4. GRANT for VACCINATION
          ```
* ```status```
  - Usage: ```status```
  - Output:
    + This will display a strip map of the Player's current city and the immediately surrounding cities.
    + It will also display the review display.
    + Maybe some more cool stuff if I can figure it out.
* ```detail```
    - Usage: ```detail <REVIEW #>``` where ```<REVIEW #>``` is the number from the list provided by the ```review``` command.
    - Output: 
        + For Grants, text describing how the grant may be used.
        + For Research, detailed information about the City described.
* ```apply```
    - Usage: ```apply <REVIEW #>```
    - Output: 
        + If ```<REVIEW #>``` is a valid Grant:
            ```
            Application for Grant successful.
            Grant funds disbursed for <GRANT TITLE>
            <BRIEF DESCRIPTION OF GRANT>
            ```
        + If ```<REVIEW #>``` is not a valid Grant:
            ```Your selection is not a valid Grant.```
* ```xm```
    - Usage: ```xm <TEXT TO BROADCAST>```
    - Posts ```<TEXT TO BROADCAST>``` to the general board for all Players to view.  ```<TEXT TO BROADCAST>``` is a free text message.

### Team-Specific Commands

#### Planning Team

* ```reapply```
    - Usage: ```reapply```
    - Output: 
        + Presents a list of Grants that are available to the **Planning Team** for re-application:
            ```
            1. <GRANT NAME>
            2. <GRANT NAME>
            3. CANCEL
            Enter a Number:
            ```

#### Dispatch Team

* ```dispatch```
    - Usage: ```dispatch <TEAM NAME> <LOCATION>```
    - Output:
        + If everything goes correctly: 
            ```
            ...Travel arrangements made for <TEAM NAME> Team to <LOCATION>
            ```
        + If the dispatched location is not valid (not a valid move for the dispatched team or no other team in the dispatched location):
            ```
            ...Invalid conditions for dispatching <TEAM NAME> to <LOCATION>.
            ```