## Overview

## Welcome to the GameScorekeeper API documentation

This document is intended as a guide and look-up reference for developers creating apps and sites powered by the GameScorekeeper
APIs.

The GameScorekeeper APIs provide data from Esports matches. There are currently two APIs available that
a user or app can connect to in order to retrieve data:

* REST API: The REST API provides access to all data on past and future fixtures, for example
  final results of matches already played and start times of scheduled matches.
* Live Data API: The live API makes it possible to establish live WebSocket connections
  with the GameScorekeeper data platform to retrieve real-time results and stats from fixtures
  currently being played.

Connecting to the APIs requires an authentication token, which is obtained by creating an account with
GameScorekeeper. Please contact us at
[email protected] to create an account.

## Terminology

## Timestamps

All timestamps are Unix-timestamps in UTC milliseconds

## Sport

A sport is an Esport, ie. a video game, supported by the GameScorekeeper data platform.

## Examples

* Counter-Strike 2
* Dota2
* League of Legends

## Competition

A competition is a group of fixtures. Competitions includes both tournaments, where matches are usually played at the same
venue over a short time span, and leagues, where matches can be played over a longer time span in a range
of geographical locations.

## Examples

* Blast Pro Series 2017
* HGC Spring 2018
* The International 2017
* 2018 NA LCS Spring Split

## Fixture

A fixture, also known as a match, represents a series of one or more games played between two or more
participants.

A fixture is part of a competition.

Each fixture has a scheduled start time. This is the planned start time for the fixture according to
the fixture organiser. Actual start time may differ from the scheduled start time.

## Examples

* Astralis vs North in Blast Pro Series 2017
* Fnatic vs Misfits in HGC Spring 2018
* Team Liquid vs Invictus Gaming in The International 2017
* Cloud9 vs Counter Logic Gaming in 2018 NA LCS Spring Split

## Participant

A participant represents a team, player or other entity participating in a fixture. Though participants
are most commonly esports teams, some sports and events feature 1v1 matches and national, regional
or all-star teams.

Participants may have individual handicaps in any given fixture.

If fixture has been scheduled, but one or more participants are "To be determined", or TBD, the REST API
will reflect this as a null value until the participants are found.

## Examples

* Team Liquid
* Life
* Brazil
* All-Stars West

## REST API https://api.gamescorekeeper.com

The REST API is used to retrieve upcoming and completed fixtures. Use Authorization: Bearer <Your Token> in the header
of a request. A missing or invalid authorization header will result in a status `401`.

The base URL for all REST API requests is
https://api.gamescorekeeper.com. Each endpoints lists its path as part of the header.

## List Sports /v1/sports

Gets all supported sports.

### Responses

### Response Schema

sports

SportDTO

name

Name of the sport.

string

alias

Alias of the sport.

string

## Example /v1/sports

```

```

## Get LoL champions /v1/sports/lol/champions

Gets a list of LoL champions.

### Responses

### Response Schema

champions

Array of Champion

name

Name of the champion.

string

title

The champion's title.

string

riotName

Riot's internal string name of the champion.

string

championId

The Riot ID of the champion.

integer

## Example /v1/sports/lol/champions

```

```

## Get Dota2 heroes /v1/sports/dota2/heroes

Gets a list of Dota2 heroes.

### Responses

### Response Schema

heroes

Array of Hero

name

Name of the hero.

string

valveName

Valve's internal string name of the champion.

string

heroId

The Valve ID of the hero.

integer

## Example /v1/sports/dota2/champions

```

```

## Get CS2 maps /v1/sports/cs2/maps

Gets a list of the CS2 map pool.

### Responses

### Response Schema

maps

Array of map

name

Name of the map.

string

active

Whether or not the map is in the current active map pool.

boolean

## Example /v1/sports/cs2/maps

```

```

## List Competitions /v1/competitions?query

Gets all competitions or optionally all competition for a given sport.

### Query Parameters

sport

The sport alias to filter on.

string

from

string or number

If set, returns only competitions with startDate **after** this timestamp.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional. No default.

to

string or number

If set, returns only competitions with endDate **before** this timestamp.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional. No default.

hasFixtures

If set to true will only return competitions that have fixtures associated with them.
Defaults to false.

boolean

### Responses

### Response Schema

competitions

Array of CompetitionDTO

id

ID of the competition.

long

name

Name of the competition.

string

sportAlias

Alias of the sport this competition is held for.

string

startDate

The timestamp for when the competition starts. Can be null.

timestamp

endDate

The timestamp for when the competition ends. Can be null.

timestamp

prizePoolUSD

The total prize pool of the competition in USD. Can be null.

integer

location

Location of the competition. Can be null.

string

organizer

Name of the competition organizer. Can be null.

string

type

Type of the competition. Valid values:
Online,
Offline,
Online/Offline,
Unknown.
Can be null.

string

fixtureCount

The number of known fixtures in this competition.

integer

derivatives

map of string -> string

An elastic map of properties that is derived from `name` of the competition.
Possible keys are, but not limited to:
year,
season,
stage,
stage\_type,
region
  
If nothing could be derived from the `name`, this map will be empty.

metadata

map of string -> string

A map of external metadata for this competition.
  
Possible keys are, but not limited to:
liquipediaTier
  
May be empty.

## Example /v1/competitions?sport=cs2&from=2024-02-05&to=2024-02-06

```

```

## Get Competition /v1/competitions/{competitionId}

Gets a single competition by its ID.

### Path Parameters

competitionId

The competition ID.

long

### Responses

### Response Schema

id

The competition ID.

long

name

The name of the competition.

string

sportAlias

The sport of the competition.

string

startDate

The timestamp for when the competition starts. Can be null.

timestamp

endDate

The timestamp for when the competition ends. Can be null.

timestamp

prizePoolUSD

The total prize pool of the competition in USD. Can be null.

integer

location

Location of the competition. Can be null.

string

organizer

Name of the competition organizer. Can be null.

string

type

Type of the competition. Valid values:
Online,
Offline,
Online/Offline,
Unknown.
Can be null.

string

fixtureCount

The number of known fixtures in this competition.

integer

derivatives

map of string -> string

An elastic map of properties that is derived from `name` of the competition.
  
Possible keys are, but not limited to:
season,
time\_of\_year,
year,
number,
stage,
stage\_type,
region
  
If nothing could be derived from the `name`, this map will be empty.

metadata

map of string -> string

A map of external metadata for this competition.
  
Possible keys are, but not limited to:
liquipediaTier
  
May be empty.

## Example /v1/competitions/4564

```

```

## Get Competition Participants /v1/competitions/{competitionId}/participants

Gets all teams participating in the specified competition.

### Parameters

### Path Parameters

competitionId

The competition ID.

long

### Responses

### Response Schema

competitionId

The competition ID.

long

participants

A list teams participating in the competition.

id

The id of the participant.

long

name

The name of the participant.

string

Array of CompetitionParticipant

## Example /v1/competitions/4564/participants

```

```

## Get Competition Stages /v1/competitions/{competitionId}/stages

Gets a list of stages in the competition.

### Parameters

### Path Parameters

competitionId

The competition ID.

long

### Responses

### Response Schema

competitionId

The competition ID.

long

stages

A list of stages in the competition.

id

The id of the stage.

long

name

The name of the stage.

string

type

The stage type. Valid values:
Groups,
Playoffs,
Swiss,
Unknown

string

Array of CompetitionStage

## Example /v1/competitions/10586/stages

```

```

## Get Stage Participants /v1/competitions/stage/{stageId}/participants

Gets a list of participants competing in the stage.

### Parameters

### Path Parameters

stageId

The stage ID.

long

### Responses

### Response Schema

stageId

The stage ID.

long

participants

A list of participants in the stage.

participantId

The id of the participant.

long

name

The name of the participant.

string

group

The name of the group if stage is of type Groups.

string

wins

Number of wins the participant has in the stage.

integer

losses

Number of losses the participant has in the stage.

integer

roundDifference

Net round difference the participant has in the stage. Can be negative.

integer

Array of StageParticipant

## Example /v1/competitions/stage/3062/participants

```

```

## Get Stage Fixtures /v1/competitions/stage/{stageId}/stagefixtures

Gets a list of stage fixtures containing stage information for individual
fixtures such as advancements and section name.

### Parameters

### Path Parameters

stageId

The stage ID.

long

### Responses

### Response Schema

stageId

The stage ID.

long

stageFixtures

A list of stage fixtures.

fixtureId

The id of the fixture.

long

stageId

The stage ID.

long

section

Name of the stage section for the fixture (e.g. "Semifinals").

long

advancement

Advancement

winner

long

The id of the fixture the winner will advance to. May be null.

loser

long

The id of the fixture the loser will advance to. May be null.

Array of StageFixture

## Example /v1/competitions/stage/3081/stagefixtures

```

```

## List Fixtures /v1/fixtures?query

Gets all fixtures fitting the parameters specified.

### Parameters

### Query Parameters

sport

The alias of the sport to filter on (use the List Sports endpoint to get alias').
  
 Optional; includes all sports if missing.

string

competitionId

The ID of the competition to filter on (use the List Competitions endpoint to get IDs).
  
 Optional; includes all competitions if missing.

string

from

string or number

The first scheduledStartTime of the period to return fixtures for.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional; defaults to midnight today in UTC.

to

string or number

The last scheduledStartTime of the period to return fixtures for.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional; defaults to midnight tomorrow in UTC.

page

The page to start from.
  
 Optional; defaults to 1.

integer

pageCount

Number of results per page.
  
 Optional; defaults to 50.
  
 **NOTE: Caps at 50.**

integer

status

Status of the fixtures to return.
  
 Optional; Valid values:
Scheduled,
Started,
Ended,
Forfeited,
Cancelled.

string

sort

Sorting of returned fixtures by scheduled start time. Defaults to ascending.
  
 Optional; Valid values:
asc,
desc.

string

### Responses

### Response Schema

fixtures

A list of fixtures matching the search criteria.

id

The id of the fixture.

long

tie

Whether this fixture ended as a tie. Optional.

boolean

winnerId

ID of the winning participant. Optional.

long

status

Valid values:
Scheduled,
Started,
Ended,
Forfeited,
Cancelled.

string

format

name

Name of the format

string

value

Value for the format. E.g. for the format "bestOf"
a value of 5 means this is a best of 5 fixture.

integer

competition

CompetitionSummaryDTO

id

long

The id of the competition

name

string

The name of the competition

derivatives

map of string -> string

An elastic map of properties that is derived from `name` of the competition.
Possible keys are, but not limited to:
year,
season,
stage,
stage\_type,
region
  
If nothing could be derived from the `name`, this map will be empty.

scheduledStartTime

Timestamp for when this fixture is scheduled to start.

timestamp

startTime

Timestamp for when this fixture actually started.

timestamp

endTime

Timestamp for when this fixture ended.

timestamp

sport

SportSummaryDTO

alias

Alias uniquely identifying the sport.

string

name

Name of the sport.

string

participants

id

The id of the participant.

long

name

The name of the participant.

string

score

Current score for this participant in the fixture - including handicap.

integer

scoreWithoutHandicap

Current score for this participant in the fixture - not including handicap.

integer

handicap

The handicap of the participant in this specific fixture. Is added to scoreWithoutHandicap to determine final score.

integer

Array of ParticipantDTO

links

rel

The link relation. Allowed values:
v2live.

integer

link

A URI pointing to the relation.

uri

Array of LinkDTO

Array of FixtureDTO

totalCount

The total number of fixtures matching the query.

integer

## Example /v1/fixtures?sport=cs2&from=2024-02-01&to=2024-02-01&page=1&pageCount=2

```

```

## List Fixtures By Competition /v1/competitions/{competitionId}/fixtures

Gets all fixtures from the specified competition.

### Parameters

### Path Parameters

competitionId

The competition ID.

long

### Query Parameters

from

string or number

The first scheduledStartTime of the period to return fixtures for.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional; defaults to Jan 1 1970.

to

string or number

The last scheduledStartTime of the period to return fixtures for.
  
 The value can either be a Unix timestamp in milliseconds or a string of the form
yyyy-mm-dd (e.g. 2017-12-31 = Dec. 31 2017).

When using date as string, it will automatically be converted to UTC.

Optional; defaults to Jan 1 2100.

page

The page to start from.
  
 Optional; defaults to 1.

integer

pageCount

Number of results per page.
  
 Optional; defaults to 50.
  
 **NOTE: Caps at 50.**

integer

### Responses

### Response Schema

fixtures

A list of fixtures matching the search criteria.

id

The id of the fixture.

long

tie

Whether this fixture ended as a tie. Optional.

boolean

winnerId

ID of the winning participant. Optional.

long

status

Valid values:
Scheduled,
Started,
Ended,
Forfeited,
Cancelled.

string

format

name

Name of the format

string

value

Value for the format. E.g. for the format "bestOf"
a value of 5 means this is a best of 5 fixture.

integer

competition

CompetitionSummaryDTO

id

long

The id of the competition

name

string

The name of the competition

derivatives

map of string -> string

An elastic map of properties that is derived from `name` of the competition.
Possible keys are, but not limited to:
year,
season,
stage,
stage\_type,
region
  
If nothing could be derived from the `name`, this map will be empty.

scheduledStartTime

Timestamp for when this fixture is scheduled to start.

timestamp

startTime

Timestamp for when this fixture actually started.

timestamp

endTime

Timestamp for when this fixture ended.

timestamp

sport

SportSummaryDTO

alias

Alias uniquely identifying the sport.

string

name

Name of the sport.

string

participants

id

The id of the participant.

long

name

The name of the participant.

string

score

Current score for this participant in the fixture - including handicap.

integer

scoreWithoutHandicap

Current score for this participant in the fixture - not including handicap.

integer

handicap

The handicap of the participant in this specific fixture. Is added to scoreWithoutHandicap to determine final score.

integer

Array of ParticipantDTO

links

rel

The link relation. Allowed values:
v2live.

integer

link

A URI pointing to the relation.

uri

Array of LinkDTO

Array of FixtureDTO

totalCount

The total number of fixtures matching the query.

integer

## Example /v1/competitions/10773/fixtures?page=1&pageCount=2

```

```

## Get Fixture /v1/fixtures/{id}

Get a specific fixture by ID.

### Parameters

### Path Parameters

fixtureId

The fixture ID.

long

### Responses

### Response Schema

id

The fixture ID.

long

tie

Whether this fixture ended as a tie. Optional.

boolean

winnerId

ID of the winning participant. Optional.

long

status

Valid values:
Scheduled,
Started,
Ended,
Forfeited,
Cancelled.

string

format

name

The name of the format

string

value

Value for the format. E.g. for the format "bestOf"
a value of 5 means this is a best of 5 fixture.

integer

FormatDTO

competition

id

integer

The id of the competition

name

string

The name of the competition

derivatives

map of string -> string

An elastic map of properties that is derived from `name` of the competition.
Possible keys are, but not limited to:
season,
time\_of\_year,
year,
number,
stage,
stage\_type,
region
  
If nothing could be derived from the `name`, this map will be empty.

CompetitionDTO

scheduledStartTime

Timestamp for when this fixture is scheduled to start.

timestamp

startTime

Timestamp for when this fixture actually started. Can be null.

timestamp

endTime

Timestamp for when this fixture ended. Can be null.

timestamp

sport

alias

The id of the sport

integer

name

The name of the sport

string

SportSummaryDTO

participants

id

The id of the participant.

long

name

The name of the participant.

string

score

Current score for this participant in the fixture - including handicap.

integer

scoreWithoutHandicap

Current score for this participant in the fixture - not including handicap.

integer

handicap

The handicap of the participant in this specific fixture. Is added to scoreWithoutHandicap to determine final score.

integer

Array of ParticipantDTO

links

rel

The link relation. Allowed values:
v2live.

integer

link

A URI pointing to the relation.

uri

Array of LinkDTO

maps

A list of objects with data for each map played in the fixture.
Map schema is game specific, see below. Can be null.

Array of maps

## Example /v1/fixtures/401283

```

```

### Map Schemas

### CS2 Map

mapDataStatus

Indicates whether this map contains verified data or aggregated data from
our live API. Valid Values:live, verified

string

status

Status of the map. Valid values: Live, Ended

string

endTime

Timestamp for when the map ended. Can be null.

timestamp

mapName

Name of the map.

string

winnerId

ID of the participant that won the map. Can be null.

long

mapNumber

The map's number within the fixture.

integer

startTime

Timestamp for when the map was started.

timestamp

roundScores

id

ID of the participant.

long

roundsWon

How many rounds the participant has won in this map.

int

halfScores

List of scores at halftime.
Contains 2-3 integers.
First two are the number of rounds won in the first and second half.
If the map went into overtime there will be a third score indicating total
number of rounds won in overtime.

Array of integer

Array of RoundScore

teamStats

A list of stats per participant/team. Can be empty.

Array of TeamStats

teamId

Id of the team.

integer

kills

Total number of kills of the team.

integer

headshots

Total number of headshots of the team.

integer

assists

Total number of assists for the team.

integer

flash\_assists

Total number of assists by flash of the team.

integer

deaths

Total number of deaths of the team.

integer

suicides

Total number of suicides of the team.

integer

entryKills

Total number of entry kills of the team.

integer

startSide

The side this team started as on this map. Valid values: CT, Terrorist

string

players

List of stats for each individual player on the team.

kills

The number of kills of the player.

integer

headshots

The number of headshots of the player.

integer

assists

The number of assists of the player.

integer

flash\_assists

The number of flash assists of the player.

integer

deaths

The number of deaths of the player.

integer

suicides

The number of suicides of the player.

integer

entryKills

The number of entry kills of the player.

integer

kpr

The average number of kills per round of the player.

float

dpr

The average number of deaths per round of the player.

float

kast

The percantage of rounds in which the player either got a kill or assist, survived the round, or was traded.

float

adr

The average amount of damage dealt per round of the player.

float

clutches

List of clutches the player performed this map.

round

The round of the clutch.

integer

type

The type of the clutch. Valid values:
1v2,
1v3,
1v4,
1v5.

string

array

array

## Example - CS2 - Fixture ID: 533124

```

```

### Dota2 Map

mapDataStatus

Indicates whether this map contains verified data or aggregated data from
our live API. Valid Values:live, verified

string

winnerId

ID of the participant that won the map. Can be null.

long

mapNumber

The map's number within the fixture.

integer

status

Status of the map. Valid values: Live, Ended

string

teamStats

teamId

ID of the team.

long

towersDestroyed

Total number of towers the team destroyed in this map.

integer

players

List of stats for each individual player on the team.

playerId

ID of the player.

long

name

The name of the player.

string

kills

The number of kills of the player.

integer

assists

The number of assists of the player.

integer

deaths

The number of deaths of the player.

integer

heroDamage

Amount of damage dealt to heroes by the player.

integer

cs

"Creep score" - The number of combined minion and monster kills for the player.

integer

denies

The number of denied minion kills.

integer

gold

Amount of gold accrued by the player.

integer

towersDestroyed

Number of towers destroyed by the player.

integer

array

Array of TeamStats

## Example - Dota2 - Fixture ID: 537512

```

```

### LoL Map

mapDataStatus

Indicates whether this map contains verified data or aggregated data from
our live API. Valid Values:live, verified

string

winnerId

ID of the participant that won the map. Can be null.

long

mapNumber

The map's number within the fixture.

integer

status

Status of the map. Valid values: Live, Ended

string

duration

The in-game duration of the map in seconds. Can be null.

integer

mapStartTime

The epoch timestamp for when the map started. Can be null.

long

mapEndTime

The epoch timestamp for when the map ended. Can be null.

long

teamStats

teamId

ID of the team.

long

side

The team's side for this map. Valid values: blue, red

string

towersDestroyed

Total number of towers the team destroyed in this map.

integer

inhibitorsDestroyed

Total number of inhibitors the team destroyed in this map. Can be null.

integer

dragonKills

Total number of dragons the team killed in this map.

integer

dragonTypes

A list detailing the types of each dragon killed. If multiple of the same dragon type
was killed it will appear multiple times in the list.
Valid values: infernal, ocean, mountain, cloud,
hextech, chemtech.

Array of strings

riftHeraldKills

Total number of rift heralds the team killed in this map. Can be null.

integer

atakhanKills

Total number of Atakhans the team killed in this map.

integer

baronKills

Total number of barons the team killed in this map.

integer

grubKills

Total number of void grubs the team killed in this map.

integer

elderDragonKills

Total number of elder dragons the team killed in this map. Can be null.

integer

goldByMinute

An array detailing total team gold by each minute of the game.
First entry is for minute 0.

Array of integers

players

List of stats for each individual player on the team.

playerId

ID of the player.

long

name

The name of the player.

string

kills

The number of kills of the player.

integer

assists

The number of assists of the player.

integer

deaths

The number of deaths of the player.

integer

championDamage

Amount of damage dealt to champions by the player.

integer

cs

"Creep score" - The number of combined minion and monster kills for the player.

integer

gold

Total amount of gold accrued by the player.

integer

goldSpent

Total of gold spent by the player. Can be null.

integer

towersDestroyed

Number of towers destroyed by the player. Can be null.

integer

dragonKills

Number of dragons secured by the player. Can be null.

integer

baronKills

Number of barons secured by the player. Can be null.

integer

array

Array of TeamStats

firsts

Map containing which teams secured the first of each major objective.

Each of these values might be null, if the data point is unavailable.

firstBlood

Object containing IDs of team and player that secured first blood.

map of string -> int

firstTower

Object containing ID of team that secured first tower.

map of string -> int

firstDragon

Object containing ID of team that secured first dragon.

map of string -> int

firstRiftHerald

Object containing ID of team that secured first rift herald.

map of string -> int

firstInhibitor

Object containing ID of team that secured first inhibitor.

map of string -> int

firstBaron

Object containing ID of team that secured first baron.

map of string -> int

Firsts

## Example - League of Legends - Fixture ID: 521113

```

```

### HoK Map

winnerId

ID of the participant that won the map. Can be null.

long

mapNumber

The map's number within the fixture.

integer

status

Status of the map. Valid values: Live, Ended

string

teamStats

teamId

ID of the team.

long

side

Team side. Valid values: blue, red.

string

kills

Total amount of kills the team made.

integer

money

Total amount of money accrued by players on the team.

integer

towersDestroyed

Total number of towers the team destroyed in this map.

integer

players

List of stats for each individual player on the team.

playerId

ID of the player.

long

name

The name of the player.

string

hero

The name of the player's hero.

string

role

The role/position of the player.
Valid values: Side Lane, Jungler,
Middle, Support.

string

kills

The number of kills of the player.

integer

assists

The number of assists of the player.

integer

deaths

The number of deaths of the player.

integer

damageDealt

Amount of damage dealt to heroes by the player.

integer

damageReceived

Amount of damage the player received from heroes.

integer

money

Amount of money accrued by the player.

integer

array

Array of TeamStats

## Example - Honor of Kings - Fixture ID: 525559

```

```

### CoD Map

winnerId

ID of the participant that won the map. Can be null.

long

mapNumber

The map's number within the fixture.

integer

status

Status of the map. Valid values: Live, Ended

string

mode

Game mode played in the map. Valid values: Hardpoint, SnD, Control

string

mapName

Name of the map.

string

mapScores

teamId

ID of the team.

long

score

Score in the map. Dependent on game mode.

integer

Array of MapScores

teamStats

teamId

ID of the team.

long

players

List of stats for each individual player on the team.

playerId

ID of the player.

long

name

The name of the player.

string

kills

The number of kills of the player.

integer

assists

The number of assists of the player.

integer

deaths

The number of deaths of the player.

integer

score

Individual player's score.

integer

timeAlive

Time spent alive in miliseconds.

integer

distanceTraveled

Units of distance traveled in the map.

integer

movementPercentage

Percentage of game time spent moving.

integer

averageSpeed

Average movement speed.

integer

objectives

Object of objective stats. Dependent on game mode.

hillTime

Amount of time spent on hill.   
Only present on Hardpoint.   
**Optional.**

integer

contestedHillTime

Amount of time spent on a contested hill.   
Only present on Hardpoint.   
**Optional.**

integer

bombsDefused

Number of bombs defused.   
Only present on SnD.   
**Optional.**

integer

bombsPlanted

Amount of time spent on a contested hill.   
Only present on SnD.   
**Optional.**

integer

sneakDefuses

Number of sneak defuses immediately after bomb plant.   
Only present on SnD.   
**Optional.**

integer

objectivesCaptured

Number of objectives captured.   
Only present on Control.   
**Optional.**

integer

objectiveTiersContributed

Number of objective tiers contributed.   
Only present on Control.   
**Optional.**

integer

combatStats

Object of player's combat stats.

aces

Number of aces claimed.

integer

shotsHit

Number of shots hit.

integer

shotsFired

Number of shots fired.

integer

headshots

Number of headshots.

integer

damageDealt

Amount of damage dealt.

integer

damageTaken

Amount of damage taken.

integer

damageHealed

Amount of damage healed.

integer

lethalsUsed

Number of lethals used.

integer

tacticalsUsed

Number of tacticals used.

integer

tradedKills

Number of traded kills.

integer

tradedDeaths

Number of traded deaths.

integer

untradedKills

Number of untraded kills.

integer

untradedDeaths

Number of untraded deaths.

integer

highestMultikill

Highest multikill claimed.

integer

highestKillStreak

Highest kill streak.

integer

friendlyFireDamage

Amount of friendly fire damage done.

integer

specialKills

Object of player's special kill stats.

wallbangs

Number of kills made through a wall.

integer

firstBloods

Number of first bloods claimed.

integer

defuserKills

Number of kills on a player defusing the bomb.

integer

planterKills

Number of kills on a player planting the bomb.

integer

revengeKills

Number of revenge kills.

integer

longshotKills

Number of longshot kills.

integer

rotationKills

Number of rotation kills.

integer

pointblankKills

Number of point blank.

integer

inVictimFoVKills

Number of kills within victim's field of view.

integer

inAttackerFoVKills

Number of kills within attacker's field of view.

integer

array

Array of TeamStats

## Example - Call of Duty - Fixture ID: 537423

```

```

### Valorant Map

winnerId

ID of the participant that won the map. Can be null.

long

mapName

Name of the map.

string

mapNumber

The map's number within the fixture.

integer

status

Status of the map. Valid values: Live, Ended

string

roundScores

id

ID of the team.

long

roundsWon

Rounds won in the map.

integer

halfScores

List of scores at halftime. Contains 2-3 integers.
First two are the number of rounds won in the first and second half.
If the map went into overtime there will be a third score indicating total
number of rounds won in overtime.

Array of Integer

Array of RoundScores

teamStats

teamId

ID of the team.

long

startSide

Starting side. Valid values: attack, defend.

string

players

List of stats for each individual player on the team.

playerId

ID of the player.

long

name

The name of the player.

string

econRating

Economy rating, indicating amount of damage dealt pr. 1k credits used.

integer

plants

Number of spikes planted.

integer

defuses

Number of spikes defused.

integer

agents

List of agents played during the map.

Array of String

clutches

type

Type of clutch. Valid values: 1v1, 1v2,
1v3, 1v4, 1v5.

string

round

Round the clutch happened in.

integer

Array of Clutch

multikills

type

Type of multikill. Valid values: 2K, 3K,
4K, 5K.

string

round

Round the multikill happened in.

integer

Array of Multikill

totalStats

Total stats across attack and defend.

kills

Number of kills.

integer

deaths

Number of deaths.

integer

asssists

Number of asssists.

integer

adr

Average damage per round.

integer

kast

KAST ratio, the percentage of rounds where the
player had a kill, assist, survived or was traded.

integer

rating

Player rating

double

firstKills

Number of rounds this player got first kill.

integer

firstDeaths

Number of rounds this player died first.

integer

avgCombatScore

Average combat score.

integer

headshotPercentage

Percentage of kills that were headshots.

integer

Object of PlayerStats

attackStats

Player's stats on attack.

Object of PlayerStats

defendStats

Player's stats on defend.

Object of PlayerStats

array

Array of TeamStats

## Example - Valorant - Fixture ID: 815645

```

```

## Get Fixture Lineup /v1/fixtures/{id}/lineup

Get the team lineups for the fixture.

For upcoming matches, these are the expected lineups. Finished fixtures will show the full verified lineup
of players, including substitutions, that participated in the fixture.

### Responses

### Response Schema

teams

A list of teams and their player lineup.

teamId

The id of the team.

long

players

A list of players in the team's lineup.

id

The id of the player.

long

name

The name of the player.

string

Array of ParticipantDTO

Array of FixtureLineup

lineupStatus

Status of the lineups.
Valid values:
expected,
verified.
Lineups are verified within 15 minutes of fixture end.

string

## Example /v1/fixtures/401283/lineup

```

```

## Get Picked/Banned Maps /v1/pickban/{id}/maps

Gets the map picks and bans for a given fixture.

Currently avaiable for map pick/bans for CS2 fixtures.

### Responses

### Response Schema

fixtureId

ID of the fixture.

long

pickban

A list of picks and bans for this fixture.

array

order

The order during pick and bans that this entry took place.

integer

teamId

ID of the team that did the pick or ban. May be null if map was picked by default.

long

pickOrBan

Whether this entry was a pick or a ban; Valid values: pick, ban

string

mapName

Name of the picked or banned map.
Valid values:
Train,
Dust2,
Overpass,
Mirage,
Cobblestone,
Vertigo,
Nuke,
Inferno,
Unknown.

string

## Example /v1/pickban/401283/maps

```

```

## Get Picked/Banned Heroes /v1/pickban/{id}/hero

Gets the hero/champion picks and bans for a given fixture.

Currently avaiable for hero/champion pick/bans for LoL and Dota2 fixtures.

### Responses

### Response Schema

fixtureId

ID of the fixture.

long

pickban

A list of hero/champion picks and bans for this fixture.

array

mapNumber

The map number of the pick/ban.

integer

order

The order during picks and bans that this entry took place.

integer

teamId

ID of the team that did the pick or ban.

long

heroId

The Valve or Riot ID of the picked/banned hero/champion.

integer

type

Whether this entry was a pick or a ban; Valid values: pick, ban

string

## Example /v1/pickban/398287/hero

```

```

## Get Fixture Metadata /v1/fixtures/{id}/metadata/{attribute}

Get a specific attribute of metadata for a specific fixture.

Right now streamUrl, hltvMatchUrl, hltvMatchId, hltvMapIds, demoUrl and gameVersion are queryable `attributes`, but more will be made available in the future.

### Fixture Metadata Attributes

### Metadata Attributes

Attribute

Notes

streamUrl

For the streamUrl attribute, not every fixture might have one. In case of no URL available, `404` will be returned.

hltvMatchUrl

The hltvMatchUrl attribute is only available for CS2 fixtures where HLTV also has the equivalent fixture in their match listings. This is only available for fixtures since April 16 2020

### Responses

### Response Schema

fixtureId

The fixture ID

long

attribute

string

Name of the attribute

value

The value of the attribute

string

## Example /v1/fixtures/401283/metadata/streamurl

```

```

## Get Fixture Streams /v1/fixtures/{id}/streams?query

Get a list of stream URLs for fixture.

### Query Parameters

filter

Filter returned streams by language.
Valid filter parameters are either two-letter ISO 639-1 language code (e.g. "en")
or a full language-country tag (e.g. "en-US")

string

### Responses

### Response Schema

fixtureId

The fixture ID.

long

streams

A list of streams for the fixture.

streamName

The name of the stream.

string

language

The language tag of the stream.

string

url

The stream url.

string

Array of FixtureStream

## Example /v1/fixtures/404202/streams?filter=pt

```

```

## Get Fixture Stats (LoL) /v1/fixtures/{id}/stats

Gets an array of maps with detailed post match team and player stats.

All IDs used for runes, items and champions are Riot's official IDs.
Detailed information on these can be acquired through Riot's Data Dragon API,
documentation found here.

### Responses

### Response Schema

mapNumber

The map's number within the fixture.

integer

teamStats

A list of stats per participant/team. Can be empty.

Array of TeamStats

teamId

Id of the team.

integer

players

List of stats for each individual player on the team.

name

The name of the player.

string

playerId

The id of the player.

integer

items

An ID array of items that the player had when the map ended.

Array of integers

level

The level player.

integer

runes

An ID array of runes that the player used.

Array of integers

trinket

The ID of the trinket the player had.

integer

position

The player position. Valid values:
Top,
Jungle,
Middle,
Bottom,
Support.

String

championId

The ID of the played champion.

integer

visionScore

Riot calculated game value indicating the amount of vision control
and vision denial the player excerted.

integer

wardsKilled

Amount of wards the player killed.

integer

wardsPlaced

Amount of wards the player placed.

integer

controlWardsPurchased

Amount of control wards the player purchased.

integer

array

## Example /v1/fixtures/398387/stats

```

```

## Get Fixture Stats (Dota2) /v1/fixtures/{id}/stats

Gets an array of maps with detailed post match team and player stats.

All IDs used for skills, items and heroes are Valve's official IDs.
Detailed information on these can be acquired through OpenDota's constants API, e.g:
item information.

### Responses

### Response Schema

mapNumber

The map's number within the fixture.

integer

teamStats

A list of stats per participant/team. Can be empty.

Array of TeamStats

teamId

Id of the team.

integer

players

List of stats for each individual player on the team.

name

The name of the player.

string

playerId

The id of the player.

integer

items

An ID array of items that the player had when the map ended.

Array of integers

backpackItems

And ID array of items the player had in the backpack when the map ended.

Array of integers

neutralItem

ID of the player's neutral item.

integer

aghanimsShard

Whether or not the player bought Aghanim's Shard.

boolean

aghanimsScepter

Whether or not the player bought Aghanim's Scepter.

boolean

level

The player level.

integer

role

The player role. Valid values:
Core,
Support.

String

heroId

The ID of the played hero.

integer

xpMin

Average xp per minute.

integer

stunTime

Total amount of stun time applied to enemy heroes in seconds.

integer

firstBlood

Whether this player acquired first blood.

boolean

roshanKills

Amount of roshan kills the player secured.

integer

towerDamage

Total damage dealt to towers.

integer

damageReceived

Total damage received from enemy heroes.

integer

campsStacked

Number of camps the player stacked.

integer

creepsStacked

Number of creeps the player stacked.

integer

skillOrder

An ID array of the skills and talents the player leveled up, in order.

Array of integers

timeToLvl6

Number of seconds into the game that the player hit lvl 6.

integer

xpByMinute

Array of total XP at each minute of the game.
Index 0 is total XP at 0 seconds into the game (is always 0).
Index 1 is the total XP at 60 seconds into the game, index 2 is 120 seconds and so on.

Array of integers

goldByMinute

Array of total gold acquired at each minute of the game.
Index 0 is total gold at 0 seconds into the game (is always 0).
Index 1 is the total gold at 60 seconds into the game, index 2 is 120 seconds and so on.

Array of integers

lastHitsByMinute

Array of total last hits at each minute of the game.
Index 0 is total last hits at 0 seconds into the game (is always 0).
Index 1 is the total last hits at 60 seconds into the game, index 2 is 120 seconds and so on.

Array of integers

deniesByMinute

Array of total denies caused at each minute of the game.
Index 0 is total denies at 0 seconds into the game (is always 0).
Index 1 is the total denies at 60 seconds into the game, index 2 is 120 seconds and so on.

Array of integers

bountyRunes

Total bounty runes activated by the player.

integer

runesCollected

Total amount of runes collected by the player.

integer

sentryWardsKilled

Amount of sentry wards the player killed.

integer

sentryWardsPlaced

Amount of sentry wards the player placed.

integer

observerWardsKilled

Amount of observer wards the player killed.

integer

observerWardsPlaced

Amount of observer wards the player placed.

integer

array

## Example /v1/fixtures/447858/stats

```

```

## Get Fixture Stats (CS2) /v1/fixtures/{id}/stats

Gets an array of maps with round history information.

### Responses

### Response Schema

mapNumber

The map's number within the fixture.

integer

roundHistory

A list of rounds containing winner information.

Array of RoundInfo

roundNumber

Round number.

integer

winnerId

Id of the team that won the round.

integer

winSide

Side that won the round.
Valid values: Terrorist, CT, Unknown.

string

winCondition

The win condition that was achieved in the round.
Valid values: elimination, bomb\_exploded, bomb\_defused,
round\_time\_expired, unknown.

string

## Example /v1/fixtures/837516/stats

```

```

## Get Fixture Stats (Valorant) /v1/fixtures/{id}/stats

Gets an array of maps with round history information.

### Responses

### Response Schema

mapNumber

The map's number within the fixture.

integer

roundHistory

A list of rounds containing winner information.

Array of RoundInfo

roundNumber

Round number.

integer

winnerId

Id of the team that won the round.

integer

winSide

Side that won the round.
Valid values: attack, defend, Unknown.

string

winCondition

The win condition that was achieved in the round.
Valid values: elimination, bomb\_exploded, bomb\_defused,
round\_time\_expired, unknown.

string

## Example /v1/fixtures/1072948/stats

```

```

## Get Team Info /v1/teams/{id}

Get general info for a team with the given ID.

### Parameters

### Query Parameters

id

The ID of the team.

long

### Responses

### Response Schema

id

The ID of the team.

long

name

Team name.

string

sport

Team sport.

string

country

The team's country of origin. May be `mixed` or `null` if it could not be determined.

string

countryISO

The teams's country of origin in ISO format. May be `mixed` or `null` if it could not be determined.

string

region

The team's region, e.g: "North America", "Europe", "CIS" etc.

string

most\_recent\_lineup

A list of players of the team's most recent lineup.
  
 **NOTE: Returns null if the team has not played a fixture in the last 3 months.**

id

The id of the player.

long

name

The name of the player.

string

Array of ParticipantDTO

## Example /v1/teams/98

```

```

## List Upcoming Fixtures /v1/teams/{teamId}/upcoming

List the upcoming / future matches of a team. Returns the fixtures of the team's future matches.

### Parameters

### Path Parameters

teamId

The ID of team to list fixtures for.

long

### Responses

### Response Schema

See List Fixtures Response

## Get Team Form /v1/participants/{teamId}/form

Get the form of a team. Returns the results of the team's most recent matches.

### Parameters

### Path Parameters

teamId

The ID of team to get form for.

long

### Query Parameters

opponent

Limit the results to only include fixtures against this team ID.
  
Optional.

integer

count

Max amount of recent matches returned.
  
Optional; defaults to 10.
  
 **NOTE: Caps at 50.**

integer

### Responses

### Response Schema

teamId

The ID of team.

long

fixtureCount

Amount of recent fixtures returned.

integer

fixtures

Array of fixture results.

fixtureId

ID of the fixture.

long

opponentId

ID of the opponent team.

long

score

Fixture score of the team.

integer

opponentScore

Fixture score of the opponent team.

integer

fixtureTime

Timestamp for when the fixture was played.

timestamp

## Example /v1/participants/98/form?opponent=367&count=5

```

```

## Get Team Metadata /v1/participants/{id}/metadata/{attribute}

Get a specific attribute of metadata for a specific team.

Right now only hltvId and hltvUrl are a queryable `attributes`, but more will be made available in the future.

### Team Metadata Attributes

### Metadata Attributes

Attribute

Notes

hltvId

For teams where we know the equivalent team on HLTV. In case of no known ID, `404` will be returned.

hltvUrl

The direct link to the teams page on HLTV if known. In case of no URL available, `404` will be returned.

### Responses

### Response Schema

participantId

The team ID

long

attribute

string

Name of the attribute

value

The value of the attribute

string

## Example /v1/participants/98/metadata/hltvUrl

```

```

## Get Stats For Team /v1/stats/team/{teamId}?query

Gets the average map stats for the players of a given team within a given time interval.

### Parameters

### Path Parameters

teamId

The ID of team to get average stats for.

long

### Query Parameters

from

Limit the results to only include stats for matches after this timestamp.
  
Optional; defaults to 90 days ago.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

to

Limit the results to only include stats for matches before this timestamp.
  
Optional; defaults to today.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

### Responses

### Response Schema

teamId

The ID of team.

long

teamName

The name of the team.

string

fixtureCount

The total number of fixtures the stats were averaged from.

integer

maps

A list of the maps played along with information on how many of the maps were won.

array

mapName

Name of the map or "default" if maps cannot be chosen in the game.

string

played

Total number of times the team has played the map.

integer

won

Total number of wins on this map for the team.

integer

duration

Time in seconds played on the map (not all games have this statistics).

integer

pickBan

Number of times the team has picked or banned a map. A map might not contain `pickBan` if it has not been neither picked nor banned by this team, but might instead be the left-over from a vote.  
**NOTE: Currently only applicable for CS2**

object

accumulatedMapStats

A map of accumulated stats played in the specified time period. Map schema is game specific, see below.

map

## Example /v1/stats/team/98?from=1633046400000&to=1643673600000

```

```

### accumulatedMapStats Schemas

### CS2 accumulatedMapStats

kills

Accumulated number of kills.

integer

deaths

Accumulated number of deaths.

integer

assists

Accumulated number of assists.

integer

flash\_assists

Accumulated number of flash assists.

integer

headshots

Accumulated number of headshots.

integer

entryKills

Accumulated number of entry kills.

integer

suicides

Accumulated number of suicides.

integer

pistolRoundWins

Accumulated number of rounds won where only pistols can be afforded.

integer

firstToWinRounds\_

Number of times the team where to first to reach a certain amount of round wins.

integer

roundsPlayed

Total rounds played. Can be divided by `fixtureCount` to calculate the maps played per match.

integer

roundsWon,  
roundsWon\_ct,  
 roundsWon\_t

Accumulated rounds won as T/CT

integer

## Example - CS2

```
{
  "teamId": 108,
  "teamName": "Astralis",
  "fixtureCount": 13,
  "maps": [ 
    ...                                                                                   
  ],
  "accumulatedMapStats": {
    "assists": 768,
    "deaths": 2162,
    "entryKills": 328,
    "firstToWinRounds_12": 17,
    "firstToWinRounds_6": 13,
    "firstToWinRounds_9": 14,
    "flash_assists": 218,
    "headshots": 1049,
    "kills": 2112,
    "pistolRoundWins": 32,
    "roundsPlayed": 600,
    "roundsWon": 320,
    "roundsWon_ct": 194,
    "roundsWon_t": 126,
    "suicides": 0
  }
}
```

### Valorant accumulatedMapStats

assists

Accumulated number of assists.

integer

deaths

Accumulated number of deaths.

integer

defuses

Accumulated number of defuses.

integer

firstDeaths

Accumulated number of times first to die.

integer

firstKills

Accumulated number of entry kills.

integer

kills

Accumulated number of kills.

integer

plants

Accumulated number of plants.

integer

## Example - Valorant

```

```

### LoL accumulatedMapStats

## Example - League of Legends

```

```

### Dota2 accumulatedMapStats

## Example - Dota2

```

```

## Get Stats For Two Teams Head-to-head /v1/stats/team/{teamId}/vs/{teamId}?query

Returns the statistics for each of the two teams, filtered for only fixtures where they have been playing against each other.

The output for each team is the same as for single team statistics

### Parameters

### Query Parameters

from

Limit the results to only include stats for matches after this timestamp.
  
Optional; defaults to 90 days ago.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

to

Limit the results to only include stats for matches before this timestamp.
  
Optional; defaults to today.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

## Get Player Info /v1/players/{id}

Get general info for player with the given ID.

### Parameters

### Query Parameters

id

The ID of the player.

long

### Responses

### Response Schema

id

The ID of the player.

long

firstName

First name of the player.

string

lastName

Last name of the player.

string

nickname

Nickname of the player.

string

age

The player's age. May be null

integer

country

The player's country of origin. May be null

string

countryISO

The player's country of origin in ISO format. May be null

string

sport

The esport that this player is attached to.

string

## Example /v1/players/163

```

```

## Get Transfers /v1/players/transfers

Get the transfers recorded within a given time interval. A transfer is a single event - a
player joining a team or leaving one - and is dated to the day it took place.

Results are returned newest first, 100 at a time. Read further pages with the
page parameter until a page comes back empty.

Currently available for League of Legends only.

### Parameters

### Query Parameters

from

Only include transfers dated on or after this timestamp.
  
Optional; defaults to 7 days before to.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

to

Only include transfers dated on or before this timestamp.
  
Optional; defaults to now.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

sportAlias

Only include transfers of players of this esport.
  
Optional; defaults to all esports.

string

playerId

Only include transfers of this player.
  
Optional.

long

teamId

Only include transfers to or from this team.
  
Optional.

long

page

The page to list.
  
Optional; defaults to 1.

integer

### Responses

### Response Schema

transfers

The transfers found, newest first.

List of Transfer

### Transfer

playerId

The ID of the player that moved.

long

type

Whether the player joined or left the team. One of
join or leave.

string

teamId

The ID of the team joined or left.

long

role

The role the player held at the team. May be null.

string

substitute

Whether the player was at the team as a substitute.

boolean

active

Whether the player was an active member of the roster. False
where they were signed to the team but not playing for it.

boolean

date

The day the transfer took place.
  
 **NOTE: Unix timestamp in miliseconds, at midnight UTC on the day itself.**

Unix timestamp

## Example /v1/players/transfers?playerId=20240&from=1733270400000

```

```

## Get Team History /v1/players/{id}/teamhistory

Get the teams a player has been at, most recent first. Where Get
Transfers gives the individual joins and leaves, this pairs them up into the spells they
describe.

Either end of a spell can be unknown: a spell the player is still in has no endDate, and
one whose join took place before our records begin has no startDate.

Currntly available for League of Legends only

.

### Parameters

### Path Parameters

id

The ID of the player.

long

### Responses

### Response Schema

playerId

The ID of the player.

long

playerName

The name of the player.

string

teamHistory

The spells the player has had at teams, most recent first.

List of TeamSpell

### TeamSpell

teamId

The ID of the team.

long

teamName

The name of the team.

string

startDate

The day the player joined the team. Null where the join took place before our records begin.
  
 **NOTE: Unix timestamp in miliseconds, at midnight UTC on the day itself.**

Unix timestamp

endDate

The day the player left the team. Null while the player is still at the team.
  
 **NOTE: Unix timestamp in miliseconds, at midnight UTC on the day itself.**

Unix timestamp

role

The role the player held at the team. May be null.

string

substitute

Whether the player was at the team as a substitute.

boolean

active

Whether the player was an active member of the roster. False
where they were signed to the team but not playing for it.

boolean

## Example /v1/players/20240/teamhistory

```

```

## Get Stats For Player /v1/stats/player/{playerId}?query

Gets the average map stats for the given player ID in the given time interval.

### Parameters

### Path Parameters

playerId

The ID of player to get average stats for.

long

### Query Parameters

from

Limit the results to only include stats for matches after this timestamp.
  
Optional; defaults to 90 days ago.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

to

Limit the results to only include stats for matches before this timestamp.
  
Optional; defaults to today.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

### Responses

### Response Schema

playerId

The ID of player.

long

playerName

The in-game name of the player.

string

fixtureCount

The total number of fixtures the stats were averaged from.

integer

mapsCount

The total number of maps/games the stats were averaged from.

integer

roundCount

The total number of rounds the stats were averaged from.  
(Games that are not played in rounds are simply assigned a single round for every map played)

integer

averagePerRound

Map schema is game specific, see below.

map

meta

A map of various properties not directly linked to the other stats for a player

map

gsk\_rating

An overall player rating based on the seven different stats, e.g. kills, deaths, assists, and damage dealt.
The rating has an average of 1.0 for all players, so everyone with a higher rating than 1.0 will be in the upper 50% percentile.

double

## Example /v1/stats/player/163

```

```

### averagePerRound Schemas

### CS2 averagePerRound

kills

Average number of kills.

double

deaths

Average number of deaths.

double

assists

Average number of assists.

double

flash\_assists

Average number of flash assists.

double

headshots

Average number of headshots.

double

entryKills

Average number of entry kills.

double

suicides

Average number of suicides.

double

adr

Average damage per round.

double

kast

Average KAST percentage.

double

## Example - CS2

```

```

### Valorant averagePerRound

adr

Average damage per round.

double

assists

Average number of assists.

double

deaths

Average number of deaths.

double

firstKills

Average number of entry kills.

double

headshotPercentage

Average percentage of headshots.

double

kast

Average KAST percentage.

double

kills

Average number of kills.

double

## Example - Valorant

```

```

### LoL averagePerRound

## Example - League of Legends

```

```

### Dota2 averagePerRound

## Example - Dota2

```

```

## Get Stats For Multiple Players /v1/stats/player?query

Gets the average map stats for multiple given player IDs in the given time interval.

IDs can either be provided as individual IDs, or, as a shortcut, be the players of a given fixture.

If a fixture ID is provided, this will take precedence over any players that might be listed as well.

### Parameters

### Query Parameters

id

The ID of a player.
  
Can be repeated multiple times to get stats for more users:
  
`?id=<player1>&id=<player2>`

long

fixture

A fixture ID.
  
Use this to list the statistics of each player of this particular fixture.
  
Takes precedence over any `id` that might also be provided in the query string.

long

from

Limit the results to only include stats for matches after this timestamp.
  
Optional; defaults to 90 days ago.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

to

Limit the results to only include stats for matches before this timestamp.
  
Optional; defaults to today.
  
 **NOTE: Unix timestamp in miliseconds.**

Unix timestamp

## Historic Live Events /v2/live/historic/{fixtureId}

Connecting to the Live API should only be used in and around the time of live matches,
but other use cases may arise, where one could use the events for an historic, i.e. past, match.

For validation, or testing, or odds calculation purposes, this endpoint for Historic Live Events could be used
to retrieve a list of the events from a specific match.

The events will be in the same order as the Live API would have sent them, and are
completely unfiltered.

### Responses

### Response Schema

events

List of frames that happend in the match.

Array of frames

size

Size of the events object

int

### HTTP Status Response Codes

### HTTP Codes

Code

Meaning

200

The events of this fixture are found and has been verified

404

We have no live data for this fixture

## Example /v2/live/historic/63039

```
{
    "events":[
        {
        "payload": {
            "fixtureId": 63039,
            "timestamp": 1584751071707,
            "participants": [
            {
                "id": "5045"
            },
            {
                "id": "9281"
            }
            ],
            "snapshotNumber": 1746
        },
        "sortIndex": 9296004,
        "type": "fixture_started"
        },
        {
        "payload": {
            "name": "map_started",
            "mapName": "de_train",
            "fixtureId": 63039,
            "mapNumber": 1,
            "timestamp": 1584751071714,
            "participants": [
            {
                "id": "5045"
            },
            {
                "id": "9281"
            }
            ],
            "snapshotNumber": 1746
        },
        "sortIndex": 9296005,
        "type": "occurrence"
        },
        [..]
    ],
    "size":387
}
```

## Historic Live Events /v1/liveapi/historic/{fixtureId}

Connecting to the Live API should only be used in and around the time of live matches,
but other use cases may arise, where one could use the events for an historic, i.e. past, match.

For validation, or testing, or odds calculation purposes, this endpoint for Historic Live Events could be used
to retrieve a list of the events from a specific match.

The events will be in the same order as the Live API would have sent them, and are
completely unfiltered.

### Responses

### Response Schema

events

List of frames that happend in the match.

Array of frames

size

Size of the events object

int

### HTTP Status Response Codes

### HTTP Codes

Code

Meaning

200

The events of this fixture are found and has been verified

404

We have no live data for this fixture

## Example /v1/liveapi/historic/63039

```
{
  "events":[
    {
      "payload": {
        "fixtureId": 63039,
        "timestamp": 1584751071707,
        "participants": [
          {
            "id": "5045"
          },
          {
            "id": "9281"
          }
        ],
        "snapshotNumber": 1746
      },
      "sortIndex": 9296004,
      "type": "fixture_started"
    },
    {
      "payload": {
        "name": "map_started",
        "mapName": "de_train",
        "fixtureId": 63039,
        "mapNumber": 1,
        "timestamp": 1584751071714,
        "participants": [
          {
            "id": "5045"
          },
          {
            "id": "9281"
          }
        ],
        "snapshotNumber": 1746
      },
      "sortIndex": 9296005,
      "type": "occurrence"
    },
    [..]
  ],
  "size":387
}
```

## Live Data API (v2) wss://api.gamescorekeeper.com/v2/live/{fixtureId}

The Live Data API uses WebSockets to push live data to clients. Each connection to the API can deliver
data for one specific fixture.

URIs for Live Data WebSockets are based on fixture IDs as such:

```
    wss://host/v2/live/<fixtureId>
```

When connecting to the WebSocket, after having authenticated, all events from the start of the fixture
are sent. This means that connecting late will not result in a loss of information, only its delay.

If there are no v2live link listed in a fixture then there
will be no live data available for that fixture.

## Protocol

The protocol of the Live Data API is simple. Data is sent in “messages” with the following structure:

```
    {
        "type": "<the type of message being sent>",
        "payload"?: <object>
    }
```

The types are explained below along with a description of the specific payloads.

The time in
timestamp is when the message was originally generated. This means that the timestamp of a specific
message will be the same regardless of when you connect to the WebSocket.

## Authentication

When connecting to a Live Data WebSocket you will receive an authentication message like this:

```
    {
        "type": "auth"
    }
```

And to authenticate you must respond with your token like this:

```
    {
        "token": "<your bearer token>"
    }
```

The bearer token to use is the same as when connecting to the REST API.

Once authenticated you will begin receiving messages representing game data for the specified fixture once
it starts. No data is received for an unstarted fixture.

## Response

```
* {
* "type": "auth"
* }
```

## Keep-alive

In order to prevent a socket from hanging, a connection will timeout after 40 seconds of inactivity.

Because games like CS2 have tactical and technical pauses/timeouts, the socket connection might experience longer inactivity
than the 40 seconds.

A simple ping/pong scheme can be implemented to ensure keeping the connection alive.

Send the plain, simple string ping, without any qoutes or JSON wrapping, on the socket,
and the server should respond with a message of type pong

We recommend to send a ping for every 30 seconds of inactivity.

## Response

```
{
    "type": "pong"
}
```

## Reconnecting

When reconnecting to the API, you can start off with the last seen sortIndex, in order to not sieve through the entire stream of events.

Just use the seen query parameter when connecting:

`wss://api.gamescorekeeper.com/v2/live/{fixtureId}/?seen={lastSeenSortIndex}`

## Fixture Started

Frames with type
fixture\_started represent that the fixture has begun:

```
    {
        "type": "fixture_started",
        "payload": {
            "snapshotNumber": <integer>,
            "fixtureId": <integer>,
            "timestamp": <timestamp>,
            "participants": [
                {
                    "id": <integer>
                },
                {
                    "id": <integer>
                }
            ],
        }
    }
```

## Example

```

```

## Score Changed

Frames with type
score\_changed indicate that the overall score for the fixture has changed. While the specific meaning
of the score is game specific the format is the same:

```
    {
        "type": "score_changed",
        "payload": {
            "scores": [
                {
                    "participantId": <id>,
                    "score": <integer>
                }
            ],
            "snapshotNumber": <integer>
            "timestamp": <timestamp>
        },
    }
```

## Example

```

```

## Occurrence

Frames with type
occurrence represent that some discreet in-game event occurred. This might be one player killing
another or the destruction of a tower. The game-specific progression of fixtures will also be announced
via occurrences.

E.g. LoL fixtures consist of a number of "games" and this will be announced via
game\_started and
game\_ended occurrences that are unique for LoL. CS2 fixtures, on the other hand, consist of
a number of "maps" themselves consisting of a number of "rounds", which again is announced via
map\_started/ended and
round\_started/ended occurrences.

The data for these specific occurrences is described in detail in the sections relating to the specific games supported.

Overall the structure of an occurrence message is as such:

```
    {
        "type": "occurrence",
        "payload": {
            "name": "<name of occurrence, e.g. game_started>",
            "timestamp": <timestamp>,
            "fixtureId": <integer>,
            <occurrence specific properties>,
            "snapshotNumber": <integer>
        },
    }
```

Note that occurrences with the same name may occur in different games. E.g. players kill each other in both
LoL and CS2 and the associated occurrence will be named
"kill" in both games but contain different data.

## Example (bomb exploded in CS2)

```

```

## Fixture Ended

Once the entire fixture has been played the
fixture\_ended message is sent containing the final score and the winner (or indication of being
tied).

```
    {
        "type": "fixture_ended",
        "payload": {
            "timestamp": <timestamp>,
            "fixtureId": <integer>
            "winnerId"?: <id>,
            "scores": [
                {
                    "participantId": <id>,
                    "score": <score as integer>
                },
                {
                    "participantId": <id>,
                    "score": <score as integer>
                }
            ],
            "isTie": <boolean>,
            "snapshotNumber": <integer>
        }
    }
```

The property
winnerId can be null if the fixture ended in a tie.

## Example

```

```

## Counter-Strike 2 Live Data API

A fixture in CS2 is made up of one or more games. Each game is played on a specific map and consists of a number of rounds.
Games are usually played as best of 24 rounds, which means that the actual number of rounds played can
vary from game to game. Game ties are allowed at some CS2 events, while other events add additional
rounds in case of a tie.

The score of a fixture is the number of games a team has won in that fixture.

## Map Started

A map started occurrence is sent when a Map (game) starts. It contains the name of the map being played along with the map-number
in the series.

### Properties

mapName

The name of the map being played on.

string

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

participants

Array of participants.

id

Id of the participant.

string

## Example

```

```

## Map Ended

A map ended occurrence is sent when a Map (game) has been decided. Either because a winner has been found, or in tournaments
that allows ties, because the map was tied.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

winnerId

The participantId of the team who won the map. May be null.

string

tie

True if the map ended as a tie.

boolean

participants

Array of participants.

id

Id of the participant.

string

score

Fixture score (number of maps won) of the participant.

integer

roundsWon

The final round score of the participant for this map.

integer

## Example

```

```

## Map Voided

When a map is restarted or otherwise nullified an occurrence with "map\_voided" is sent. This occurrence indicates that all events between the
last map\_started and the map\_voided were not officially part of the match.

## Example

```

```

## Round Started

In CS2, a map is played over a series of up to 24 rounds or more (if it goes to overtime). When a new round starts a round started event is sent as an occurrence.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

roundNumber

The round being played in the current map.

integer

## Example

```

```

## Round Ended

When a round is concluded an occurrence with "round\_ended" is sent. The round ended occurrences summarizes how many rounds
each participant has won.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

halfNumber

The half currently being played. Switching sides during overtime also counts as halves.

integer

roundNumber

The round being played in the current map.

integer

winnerId

The ID of the participant that won the round.

string

winCondition

The condition under which the team won the round.
Valid values:
elimination,
bomb\_defused,
bomb\_exploded,
round\_time\_expired,
unknown.

string

participants

Array of participants.

id

Id of the participant.

string

roundsWon

Number of rounds won so far in the current map

integer

## Example

```

```

## Round Voided

When a round is restarted or otherwise nullified an occurrence with "round\_voided" is sent. This occurrence indicates that all events between the
last round\_started and the round\_voided were not officially part of the match.

## Example

```

```

## Half Started

A half started occurrence is sent when a half has started which is at the start of a map and every time the teams switch sides (at the start of round 16 and during overtime).

### Properties

participants

Array of participants.

id

Id of the participant.

string

side

Side of the participant for this half.
CT or
Terrorist.

string

## Example

```

```

## Half Ended

A half ended occurrence is sent when a half has ended and the teams will switch sides, or the map is over.

## Example

```

```

## Half Voided

When a half is restarted or otherwise nullified an occurrence with "half\_voided" is sent. This occurrence indicates that all events between the
last half\_started and the half\_voided were not officially part of the match.

## Example

```

```

## Kill

A
kill Occurrence is sent when a kill is detected.

### Properties

killer

player

id

The GameScorekeeper ID of the player who performed the kill.

string

name

The name of the killer.

string

side

The side the killer plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the killer plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

weapon

The weapon used to perform the kill.

string

headshot

Whether the kill was a headshot or not.

boolean

penetrated

Whether the kill was through a wall or object.

boolean

noScope

Whether the kill was made with a scopes weapon while unscoped.

boolean

whileBlinded

Whether the kill was made while blinded by a flashbang.

boolean

throughSmoke

Whether the kill was done through a smoke grenade.

boolean

killId

The ID of the kill.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Assist

An assist Occurrence is sent when an assist to a kill is detected.

### Properties

assister

player

id

The GameScorekeeper ID of the player who performed the assist.

string

name

The name of the assister.

string

side

The side the assister plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the assister plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

killId

The ID of the kill that was assisted.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Flash Assist

A flash\_assist Occurrence is sent when a flash assist to a kill is detected.

### Properties

assister

player

id

The GameScorekeeper ID of the player who performed the flash assist.

string

name

The name of the flash assister.

string

side

The side the flash assister plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the flash assister plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

killId

The ID of the kill that was flash assisted.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Suicide

A suicide Occurrence is sent when a player suicide is detected.

### Properties

player

player

id

The GameScorekeeper ID of the player who suicided.

string

name

The name of the suicider.

string

side

The side the suicider plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the suicider plays for.

string

roundNumber

The round in which the suicide happened.

integer

## Example

```

```

## Bomb Planted

A Bomb Planted Occurrence is sent when the bomb is planted.

### Properties

planter

player

id

The GameScorekeeper ID of the player who planted the bomb.

string

name

The name of the player who planted the bomb.

string

side

The side the player. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team who planted the bomb.

string

bombSite

The site the bomb was planted at.
Valid values: A, B, Unknown

string

roundNumber

The round in which the bomb plant happened.

integer

timestamp

The actual time the bomb was planted.

timestamp

## Example

```

```

## Bomb Exploded

A Bomb Exploded Occurrence is sent when the bomb explodes.

### Properties

name

The name of the occurrence: "bomb\_exploded"

string

timestamp

The actual time the bomb exploded.

timestamp

roundNumber

The round in which the bomb explode happened.

integer

## Example

```

```

## Equipment State

A snapshot of the players at that instance. The payload contains useful player information such as money and equipment,
and is automaticially broadcasted at the end of a round unless otherwise specified.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

halfNumber

The half currently being played. Switching sides during overtime also counts as halves.

integer

roundNumber

The round being played in the current map.

integer

players

Array of players.

name

Name of the player.

string

teamId

ID of the player's team.

string

playerId

ID of the player.

string

money

Money of the player.

integer

kevlar

Whether or not the player has kevlar.

boolean

helmet

Whether or not the player has helmet.

boolean

defuseKit

Whether or not the player has defuse kit.

boolean

primaryWeapon

The player's primary weapon. May be null.

string

## Example

```

```

## Full State

Receiving "full state" event for CS2 when connecting to the Live API:

Simply adding the query parameter **eventTypes** along with the value **cs\_full\_state**,

like so: `wss://api.gamescorekeeper.com/v2/live/{fixtureID}?eventTypes=cs_full_state`

This will provide the regular events for CS2 along with the new event type "full\_state", which is sent every 10 seconds. This event includes the full picture of the game at that point in time in comparison to the incremental changes of the regular events.

This query parameter only works for CS2. It has no effect on any other game, and will simply be ignored if provided.

### Properties

mapNumber

integer

1st map in a series is mapNumber 1, second is 2 etc.

roundNumber

The round in which the bomb plant happened.

integer

timestamp

The actual time the bomb was planted.

timestamp

ct

FullStateTeam

id

The GameScorekeeper ID of the team.

string

name

The name of the team.

string

players

An array of player objects for the team.

Array of FullStatePlayer

id

The GameScorekeeper ID of the player.

string

name

The name of the player.

string

kills

Number of kills the player has.

integer

deaths

Number of deaths the player has.

integer

assists

Number of assists the player has.

integer

headshots

Number of headshots the player made.

integer

suicides

Total number of suicides of the player.

integer

flashAssists

Number of flash assists the player made.

integer

defuseKit

Whether or not the player has a defuse kit.

boolean

kevlar

Whether or not the player has a kevlar vest.

boolean

helmet

Whether or not the player has a helmet.

boolean

primaryWeapon

Name of the primary weapon the player possesses.

string

hp

Number of HP the player has left (between 0 and 100).

integer

money

Amount of money the player has.

integer

dpr

Average damage per round for the player in the current map.

double

clutchWins

Amount of 1vX clutches the player has won this map.

integer

entryKills

Amount of entry kills the player has made this map.

integer

bombPlanted

Amount of bombs the player has planted this map.

integer

bombDefused

Amount of bombs the player has defused this map.
**NOTE: Currently unavailable, will always be 0.**

integer

terrorist

FullStateTeam

## Example

```

```

## League of Legends Live Data API (v2)

A LoL fixture is made up of a number of games. For consistency with other live API's,
a game is called a map in the occurrences

The score of a fixture is the number of games a team has won in that fixture.

## Map Started

The map started occurrence contains information on the side of the participants (blue/red).

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

participants

Array of participants.

id

Id of the participant.

string

side

The side of the participant. Can be
blue or
red.

string

## Example

```

```

## Map Ended

A Map ended occurrence is sent when we have detected a game has ended. The winnerId refers to the ID of the participant who
won the game.

### Properties

mapNumber

integer

The map number that has ended

## Example

```

```

## Map Winner

A Map winner occurrence is sent when we have detected the winner of a map. The winnerId refers to the ID of the participant who
won the game.

### Properties

mapNumber

integer

The map number that a winner has been detected for

winnerId

The participantId of the team who won the game.

string

teamName

The name the team who won the game.

string

participants

Array of participants.

id

Id of the participant.

string

score

Fixture score (number of games won) of the participant.

integer

name

Id name the participant.

string

## Example

```

```

## Kill

The kill occurrence is sent when a champion takedown takes place.

### Properties

gameNumber

integer

1st game in a series is gameNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

killer

player

id

The GameScorekeeper ID of the player who performed the kill.

string

name

The name of the killer.

string

teamId

The GameScorekeeper ID of the team the killer plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

assists

array of player

id

The GameScorekeeper ID of the player who assisted the kill.

string

name

The name of the assister.

string

teamId

The GameScorekeeper ID of the team the asisster plays for.

string

## Example

```

```

## Tower Destroyed

The tower destroyed occurrence is sent when team destroys an enemy turret.

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

teamId

string

The GameScorekeeper ID of the team destroying the tower.

## Example

```

```

## Inhibitor Destroyed

The Inhibitor destroyed occurrence is sent when team destroys an enemy inhibitor.

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

teamId

string

The GameScorekeeper ID of the team destroying the inhibitor.

## Example

```

```

## Dragon Slain

The dragon slain occurrence is sent when team kills a dragon.

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

teamId

string

The GameScorekeeper ID of the team killing the dragon.

dragon

string

The dragon type being slain.
Valid values:
Ocean,
Infernal,
Mountain,
Cloud,
Elder

## Example

```

```

## Baron Slain

The Baron Slain occurrence is sent when team kills a Baron Nashor.

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

teamId

string

The GameScorekeeper ID of the team killing the baron.

## Example

```

```

## Full State

The full state occurrence is sent every 10 seconds during a game.

### Properties

gameNumber

integer

1st game in a series is gameNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

blueTeam

FullStateTeam

id

The GameScorekeeper ID of the team.

string

name

The name of the team.

string

totalKills

Total amount of kills the team has.

integer

totalGold

Total amount of gold the team has.

integer

towers

The number of towers destroyed by the team.

integer

inhibitors

The number of inhibitors destroyed by the team.

integer

dragons

A list of dragons slain by the team. Valid values:
ocean,
infernal,
mountain,
cloud,
elder

array of strings

barons

The number of barons slain by the team.

integer

players

An array of player objects for the team.

Array of FullStatePlayer

id

The GameScorekeeper ID of the player.

string

name

The name of the player.

string

role

The role of the player in the match.
Valid values:
top,
jungle,
mid,
bottom,
support
.

string

championName

The champion the player is playing.

string

kills

Number of kills the player has.

integer

deaths

Number of deaths the player has.

integer

assists

Number of assists the player has.

integer

cs

CS (also known as Creep Score) - a score indicating the amount of
minions and monsters the player has slain.

integer

totalGold

Total amount of gold accrued by the player in the game.

integer

level

Level of the player in the game.

integer

currentHealth

Current amount of health the player has.

integer

maxHealth

Max amount of health the player has.

integer

redTeam

FullStateTeam

## Example

```

```

## Dota2 Live Data API (v2)

A Dota2 fixture is made up of a number of games. For consistency with other live API's,
a game is called a map in the occurrences

The score of a fixture is the number of games a team has won in that fixture.

## Map Started

The map started occurrence contains information on the side of the participants (radiant/dire).

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

participants

Array of participants.

id

Id of the participant.

string

side

The side of the participant. Can be
rdiant or
dire.

string

## Example

```

```

## Map Ended

A Map ended occurrence is sent when we have detected a game has ended. The winnerId refers to the ID of the participant who
won the game.

### Properties

mapNumber

integer

The map number that has ended

## Example

```

```

## Map Winner

A Map winner occurrence is sent when we have detected the winner of a map. The winnerId refers to the ID of the participant who
won the game.

### Properties

mapNumber

integer

The map number that a winner has been detected for

winnerId

The participantId of the team who won the game.

string

teamName

The name the team who won the game.

string

participants

Array of participants.

id

Id of the participant.

string

score

Fixture score (number of games won) of the participant.

integer

name

Id name the participant.

string

## Example

```

```

## Full State

The full state occurrence is sent every 5 seconds during a game.

### Properties

mapNumber

integer

1st game in a series is mapNumber 1, second is 2 etc.

gameTime

integer

Amount of seconds elapsed in-game.

radiant

FullStateTeam

id

The GameScorekeeper ID of the team.

string

name

The name of the team.

string

totalKills

Total amount of kills the team has.

integer

totalGold

Total amount of gold the team has.

integer

players

An array of player objects for the team.

Array of FullStatePlayer

id

The GameScorekeeper ID of the player.

string

name

The name of the player.

string

heroId

The ID of the hero the player is playing.

string

kills

Number of kills the player has.

integer

deaths

Number of deaths the player has.

integer

assists

Number of assists the player has.

integer

lastHits

A score indicating the amount of creeps
the player has slain.

integer

denies

The amount of creeps denied.

integer

totalGold

Total amount of gold accrued by the player in the game.

integer

level

Level of the player in the game.

integer

goldPerMin

Average amount of gold earned pr. minute in the game.

integer

xpPerMin

Average amount of XP earned pr. minute in the game.

integer

items

List IDs of items the player possesses.

array

dire

FullStateTeam

## Example

```

```

## Live Data API (v1) (deprecated) wss://api.gamescorekeeper.com/v1/liveapi/{fixtureId}

This version of the Live API is no longer maintained, and is therefore deprecated.

Please use v2 as the primary source of live events.

It is recommended to only use this version where high-availability is needed, and as such only for backup,
if v2 seems unresponsive.

---

The Live Data API uses WebSockets to push live data to clients. Each connection to the API can deliver
data for one specific fixture.

URIs for Live Data WebSockets are based on fixture IDs as such:

```
    wss://host/v1/liveapi/<fixtureId>
```

When connecting to the WebSocket, after having authenticated, all events from the start of the fixture
are sent. This means that connecting late will not result in a loss of information, only its delay.

## Protocol

The protocol of the Live Data API is simple. Data is sent in “messages” with the following structure:

```
    {
        "type": "<the type of message being sent>",
        "payload"?: <object>
    }
```

The types are explained below along with a description of the specific payloads.

The time in
timestamp is when the message was originally generated. This means that the timestamp of a specific
message will be the same regardless of when you connect to the WebSocket.

## Authentication

When connecting to a Live Data WebSocket you will receive an authentication message like this:

```
    {
        "type": "auth"
    }
```

And to authenticate you must respond with your token like this:

```
    {
        "token": "<your bearer token>"
    }
```

The bearer token to use is the same as when connecting to the REST API.

Once authenticated you will begin receiving messages representing game data for the specified fixture once
it starts. No data is received for an unstarted fixture.

## Response

```
* {
* "type": "auth"
* }
```

## Keep-alive

In order to prevent a socket from hanging, a connection will timeout after 40 seconds of inactivity.

Because games like CS2 have tactical and technical pauses/timeouts, the socket connection might experience longer inactivity
than the 40 seconds.

A simple ping/pong scheme can be implemented to ensure keeping the connection alive.

Send the plain, simple string ping, without any qoutes or JSON wrapping, on the socket,
and the server should respond with a message of type pong

We recommend to send a ping for every 30 seconds of inactivity.

## Response

```
{
    "type": "pong"
}
```

## Reconnecting

When reconnecting to the API, you can start off with the last seen sortIndex, in order to not sieve through the entire stream of events.

Just use the seen query parameter when connecting:

`wss://api.gamescorekeeper.com/v1/liveapi/{fixtureId}/?seen={lastSeenSortIndex}`

## Fixture Started

Frames with type
fixture\_started represent that the fixture has begun:

```
    {
        "type": "fixture_started",
        "payload": {
            "snapshotNumber": <integer>,
            "fixtureId": <integer>,
            "timestamp": <timestamp>,
            "participants": [
                {
                    "id": <integer>
                },
                {
                    "id": <integer>
                }
            ],
        }
    }
```

## Example

```

```

## Score Changed

Frames with type
score\_changed indicate that the overall score for the fixture has changed. While the specific meaning
of the score is game specific the format is the same:

```
    {
        "type": "score_changed",
        "payload": {
            "scores": [
                {
                    "participantId": <id>,
                    "score": <integer>
                }
            ],
            "snapshotNumber": <integer>
            "timestamp": <timestamp>
        },
    }
```

## Example

```

```

## Occurrence

Frames with type
occurrence represent that some discreet in-game event occurred. This might be one player killing
another or the destruction of a tower. The game-specific progression of fixtures will also be announced
via occurrences.

E.g. LoL fixtures consist of a number of "games" and this will be announced via
game\_started and
game\_ended occurrences that are unique for LoL. CS2 fixtures, on the other hand, consist of
a number of "maps" themselves consisting of a number of "rounds", which again is announced via
map\_started/ended and
round\_started/ended occurrences.

The data for these specific occurrences is described in detail in the sections relating to the specific games supported.

Overall the structure of an occurrence message is as such:

```
    {
        "type": "occurrence",
        "payload": {
            "name": "<name of occurrence, e.g. game_started>",
            "timestamp": <timestamp>,
            "fixtureId": <integer>,
            <occurrence specific properties>,
            "snapshotNumber": <integer>
        },
    }
```

Note that occurrences with the same name may occur in different games. E.g. players kill each other in both
LoL and CS2 and the associated occurrence will be named
"kill" in both games but contain different data.

## Example (bomb exploded in CS2)

```

```

## Fixture Ended

Once the entire fixture has been played the
fixture\_ended message is sent containing the final score and the winner (or indication of being
tied).

```
    {
        "type": "fixture_ended",
        "payload": {
            "timestamp": <timestamp>,
            "fixtureId": <integer>
            "winnerId"?: <id>,
            "scores": [
                {
                    "participantId": <id>,
                    "score": <score as integer>
                },
                {
                    "participantId": <id>,
                    "score": <score as integer>
                }
            ],
            "isTie": <boolean>,
            "snapshotNumber": <integer>
        }
    }
```

The property
winnerId can be null if the fixture ended in a tie.

## Example

```

```

## Counter-Strike Global Offensive (CS2) Live Data API

A fixture in CS2 is made up of one or more games. Each game is played on a specific map and consists of a number of rounds.
Games are usually played as best of 24 rounds, which means that the actual number of rounds played can
vary from game to game. Game ties are allowed at some CS2 events, while other events add additional
rounds in case of a tie.

The score of a fixture is the number of games a team has won in that fixture.

## Map Started

A map started occurrence is sent when a Map (game) starts. It contains the name of the map being played along with the map-number
in the series.

### Properties

mapName

The name of the map being played on.

string

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

participants

Array of participants.

id

Id of the participant.

string

## Example

```

```

## Map Ended

A map ended occurrence is sent when a Map (game) has been decided. Either because a winner has been found, or in tournaments
that allows ties, because the map was tied.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

winnerId

The participantId of the team who won the map. May be null.

string

tie

True if the map ended as a tie.

boolean

participants

Array of participants.

id

Id of the participant.

string

score

Fixture score (number of maps won) of the participant.

integer

roundsWon

The final round score of the participant for this map.

integer

## Example

```

```

## Round Started

In CS2, a map is played over a series of up to 24 rounds or more (if it goes to overtime). When a new round starts a round started event is sent as an occurrence.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

roundNumber

The round being played in the current map.

integer

## Example

```

```

## Round Ended

When a round is concluded an occurrence with "round\_ended" is sent. The round ended occurrences summarizes how many rounds
each participant has won.

### Properties

mapNumber

1st map of a fixture is mapNumber 1, second is 2 etc.

integer

winnerId

The ID of the participant that won the round.

string

winCondition

The condition under which the team won the round.
Valid values:
elimination,
bomb\_defused,
bomb\_exploded,
round\_time\_expired,
unknown.

string

participants

Array of participants.

id

Id of the participant.

string

roundsWon

Number of rounds won so far in the current map

integer

playerEquipment

Array of players.

name

Name of the player.

string

teamId

ID of the player's team.

string

playerId

ID of the player.

string

money

Money of the player.

integer

kevlar

Whether or not the player has kevlar.

boolean

helmet

Whether or not the player has helmet.

boolean

defuseKit

Whether or not the player has defuse kit.

boolean

primaryWeapon

The player's primary weapon. May be null.

string

## Example

```

```

## Round Voided

When a round is restarted or otherwise nullified an occurrence with "round\_voided" is sent. This occurrence indicates that all events between the
last round\_started and the round\_voided were not officially part of the match.

## Example

```

```

## Half Started

A half started occurrence is sent when a half has started which is at the start of a map and every time the teams switch sides (at the start of round 16 and during overtime).

### Properties

participants

Array of participants.

id

Id of the participant.

string

side

Side of the participant for this half.
CT or
Terrorist.

string

## Example

```

```

## Half Ended

A half ended occurrence is sent when a half has ended and the teams will switch sides, or the map is over.

## Example

```

```

## Half Voided

When a half is restarted or otherwise nullified an occurrence with "half\_voided" is sent. This occurrence indicates that all events between the
last half\_started and the half\_voided were not officially part of the match.

## Example

```

```

## Kill

A
kill Occurrence is sent when a kill is detected.

### Properties

killer

player

id

The GameScorekeeper ID of the player who performed the kill.

string

name

The name of the killer.

string

side

The side the killer plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the killer plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

weapon

The weapon used to perform the kill.

string

headshot

Whether the kill was a headshot or not.

boolean

killId

The ID of the kill.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Assist

An assist Occurrence is sent when an assist to a kill is detected.

### Properties

assister

player

id

The GameScorekeeper ID of the player who performed the assist.

string

name

The name of the assister.

string

side

The side the assister plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the assister plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

killId

The ID of the kill that was assisted.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Flash Assist

A flash\_assist Occurrence is sent when a flash assist to a kill is detected.

### Properties

assister

player

id

The GameScorekeeper ID of the player who performed the flash assist.

string

name

The name of the flash assister.

string

side

The side the flash assister plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the flash assister plays for.

string

victim

player

id

The GameScorekeeper ID of the player who was killed.

string

name

The name of the victim.

string

side

The side the victim plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the victim plays for.

string

killId

The ID of the kill that was flash assisted.

string

roundNumber

The round in which the kill happened.

integer

## Example

```

```

## Suicide

A suicide Occurrence is sent when a player suicide is detected.

### Properties

player

player

id

The GameScorekeeper ID of the player who suicided.

string

name

The name of the suicider.

string

side

The side the suicider plays for. "CT" or "TERRORIST".

string

teamId

The GameScorekeeper ID of the team the suicider plays for.

string

roundNumber

The round in which the suicide happened.

integer

## Example

```

```

## Bomb Planted

A Bomb Planted Occurrence is sent when the bomb is planted.

### Properties

planterId

The GameScorekeeper ID of the player who planted the bomb.

string

planterName

The name of the player who planted the bomb.

string

roundNumber

The round in which the bomb plant happened.

integer

sourceTeamId

The GameScorekeeper ID of the team who planted the bomb.

string

targetTeamId

The GameScorekeeper ID of the team who had the bomb planted against them.

string

timestamp

The actual time the bomb was planted.

timestamp

## Example

```

```

## Bomb Defused

A Bomb Defused Occurrence is sent when the bomb is defused.

### Properties

name

The name of the occurrence: "bomb\_defused"

string

defuserId

The GameScorekeeper ID of the player who defused the bomb.

string

defuserName

The name of the player who defused the bomb.

string

roundNumber

The round in which the bomb defuse happened.

integer

sourceTeamId

The GameScorekeeper ID of the team who defused the bomb.

string

targetTeamId

The GameScorekeeper ID of the team whose bomb was defused.

string

timestamp

The actual time the bomb was defused.

timestamp

## Example

```

```

## Bomb Exploded

A Bomb Exploded Occurrence is sent when the bomb explodes.

### Properties

name

The name of the occurrence: "bomb\_exploded"

string

timestamp

The actual time the bomb exploded.

timestamp

roundNumber

The round in which the bomb explode happened.

integer

sourceTeamId

The GameScorekeeper ID of the team who successfully had the bomb explode.

string

targetTeamId

The GameScorekeeper ID of the team who failed to defuse the bomb in time.

string

## Example

```

```

## Image API https://img.gamescorekeeper.com

The Image API can be used to retrieve miscellaneous logos for teams/players or pictures referenced in other endpoints.

This API is also restricted, and you need to use Authorization: Bearer <Your Token> in the header
of a request. A missing or invalid authorization header will result in a status `401`.

The base URL for all Image API requests is
https://img.gamescorekeeper.com.

Even though the images of this service are cached, it is urged to not reference this API directly in your application, and cache all results at
your own end.

## Team Logos /logo/participant/{participantId}

Retrieve the logo of a team by their ID

Team logos are rarely updated, so an interval of ten days is recommended as the least amount of time to cache.

We strive to have every logo in SVG, but as this is not always possible, the Content-Type header will always tell the format of a specific image.

## ID Matching API https://ext.gamescorekeeper.com

The matching API can be used to connect companies, where the IDs are not the same between them.

Currently, this includes finding the corresponding IDs of Oddin.gg API(s) to GameScorekeeper API(s) and vice versa.

Users need to provide the Authorization header, as with all of the API requests, and it would be preferable for the users to also provide a custom User-Agent header to identify your service more cleanly.

## Oddin.gg / GameScorekeeper /v1/matching/oddin/{type}

### Matching types

type

Notes

fixtures

Used to find connections between GSK fixtures and Oddin.gg matches.

teams

Used to find connections between teams.

competitions

Used to find connections between GSK competitions and Oddin.gg tournaments.

players

Used to find connections between players.

### Query Parameters

oddin\_id

A single or multiple Oddin.gg IDs.

string

gsk\_id

A single or multiple GSK IDs.

string

Both of the query parameters can be present in the same request.

All the IDs can either be single or multiple separated by commas, like so  
 `/fixtures?gsk_id=1079188,1081143,1075606&oddin_id=3232705`

### Responses

### Response Schema

list

List of ID connections between the two companies.

Array of connections

Oddin.gg might have multiple IDs for the same type (fixture, team, competition), so the mapping is a list of possible connections.

## Example /v1/matching/oddin/fixtures?gsk\_id=1079188,1081143,1075606&oddin\_id=3232705

```
[
  {
    "company": "gsk",
    "original": 1079188,
    "connections":
    [
      3344237
    ]
  },
  {
    "company": "gsk",
    "original": 1081143,
    "connections":
    [
      3345581
    ]
  },
  {
    "company": "gsk",
    "original": 1075606,
    "connections":
    [
      3232703,
      3232705
    ]
  },
  {
    "company": "oddin",
    "original": 3232705,
    "connections":
    [
      1075606
    ]
  }
]
```

## Frequently Asked Questions

## Rate limiting

We do not currently enforce a hard limit on the API usage, but we do encourage our users to adhere to the following limitations:

**REST API**: 1,000 requests per hour. If needed, we can up this limit on a per-user basis.

**Live API**: A single websocket connection per fixture. This can also be increase on a per-user basis.

We reserve the right to contact the user, if we monitor a large number of requests from a single user.