const core = require('@actions/core');
const github = require('@actions/github');

try{
    core.debug('Debug message');
    core.warning('Warning message');
    core.error('Error message');
    core.setSecret('This is a secret');
    
    const name =  core.getInput('who_to_greet');
    
    console.log(`Hello ${name}!`);
    
    const time = (new Date()).toTimeString();
    core.setOutput("time", time);
    core.exportVariable('HELLO_TIME', time);

    core.startGroup("logging github context");
    console.log(JSON.stringify(github.context, null, 2));
    core.endGroup();
    
} catch (error) {
    core.setFailed(error.message);
}

