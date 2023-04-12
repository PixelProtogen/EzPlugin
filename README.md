# EzPlugin
Easy to use wacky program made for making MCreator plugins.
short usage tuttorial

Creating/Opening Plugin folder
on first opening you will get message about config file being created in D:\ path
after that you need to type path and name of file
example: D:\EzPlugin
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
after that you will get in main menu with includes:

Plugin info
Procedures
Localization

About plugin info its easy to use and doesnt require explanation
expect id keep it without any special characters like space , question mark and etc
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
now on Procedures
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
after you open it you will see new window called selection
we will talk about it later
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Procedure frame contains text field , New Procedure button and New Class Button
text field determines name of Class or Procedure
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
about Class or category
Classes needs for sorting procedures like in other plugins or Mcreator itself (Block data,Block managment,Command parameters...)
Upon creating Class or Procedure new object will appear in Selection with its icon

when you click on any (not image) option 
selection window will close and main frame will update having color field , api type toggle , remove button and save button

api moves Class to bottom where advanced category is
color can be 1 or 360 more about it here
developers.google.com/blockly/guides/create-custom-blocks/block-colour
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
now about Procedures
On opening 1 more window will appear
Code Editor. Like always later about it

procedure made of 6 varibles and arguments

color (we already talked about it)
Inline (makes you block appear with stuff in line)
Output (returning value type if it does return something)
Prev Statement (needs for joining for previous blocks)
Next Statement (need for joining for next blocks)
Toolbox (Block class)

quick about varible you can type in:
color - number only
Inline - True or False or null
Output - VaribleName or None or null
Prev Statement - null or None
Next Statement - null or None
Toolbox - Class 

null - can be any varible
None - removes varible completely disabling it 
VarbielName - can be "String" , "Number" , "Boolean" and much more like block , itemstacks and etc
Class - name of Class you made (without $)
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
small note:
if you making block like [Get block at x,y,z]
you would need to set Prev and Next Statement to None and keep Output
if you making block like [Place (block) at x,y,z]
you would need to set Output to None and keep Prev and Next as null
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
now onto arguments
arguments used for inputing varibles,texts and other blocks
to create one you need give it a name (textbox near New Statement)
after that it will appear in Selection with its icon

upon opening arg 3 fields and remove button will appear:
Type (type of argument)
Name (Optional for determining arg)
Check (not optional and can be any varible or None)

Types can be:
input_value - for other blocks inside our block like in [Get block at x,y,z]
field_input - text field for stuff to type
input_statement - for other blocks like IF block does

if type was not correct then question mark icon will apear near arg
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Code Editor
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Code editor name speaks for itself so im gonna go about main stuff:
code ${type$name} will get arg value

examples:
argument - type:"input_value" name:"iv"
code - ${input$iv}

argument - type:"field_input" name:"fi"
code - ${field$fi}

argument - type:"input_statement" name:"is"
code - ${statement$is}

finally we finished with Procedures and now onto 
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Localization 
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Localization needs for describing procedure text and arg positions
upon opening localization selection window will open with all procedures and classes to edit

after selecting class or procedure text field will appear where you type text that will be desplayed
for procedures its diffrent
to desplay args you need %[arg_pos]
example: "place block at x:%1 y:%2 z:%3"
arg position counts from up to down in arg selection window
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Finished Plugin Foder 
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
after you finish work with plugin and want to test it
you need to have WinRAR or anything that can archive stuff

after locating you plugin folder you need to open it, select all stuff inside and archive everything as .zip

welp i think thats all so yea goodluck with you plugin
