import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  IFileBrowserFactory
} from '@jupyterlab/filebrowser';

import { Terminal } from '@jupyterlab/terminal';

const commandId = 'submit2coursera:sendAssignment';

/**
 * Initialization data for the Submit-2-Coursera command.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'sendAssignment',
  autoStart: true,
  requires: [
    IFileBrowserFactory
  ],
  activate: (app: JupyterFrontEnd, factory: IFileBrowserFactory) => {
    const { commands } = app;
    const { tracker } = factory;

    // Add a command to process the submit
    commands.addCommand(commandId, {
      label: 'Submit Coursera Assignment',
      caption: 'Submit current Coursera Assignment',
      execute: async args => {
        console.log("Submit Coursera Assignment Start");
        const widget = tracker.currentWidget;
        const model = widget?.selectedItems().next();
        if (!model) {
          return;
        }
        console.log(model.path);
        const s1 = await app.serviceManager.terminals.startNew();
        const term1 = new Terminal(s1);
        term1.title.closable = true;
        app.shell.add(term1,'main');
        
        const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
        while(term1.session.connectionStatus != "connected") {
          await delay(1000);
        }
        const cookie = document.cookie.replace(/(?:(?:^|.*;\s*)COURSERA_SUBMISSION_TOKEN\s*\=\s*([^;]*).*$)|^.*$/, "$1");
        term1.session.send({ 
          type: 'stdin', 
          content: ['submit.py '+ model.path + ' ' + cookie + '\n'] 
        });
        
      }
    });

    // Add the right-click option to the Notebook pop-up
    app.contextMenu.addItem({
      command: commandId,
      rank: 99,
      selector: '.jp-DirListing-item'
    });
    console.log('Added command: '+commandId);
  }
};


export default extension;
