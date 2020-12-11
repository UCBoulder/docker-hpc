# Submit-2-Coursera

This is a small plug-in that adds a context menu (right-click) on a Jupyter Notebook to submit the Notebook to the active Coursera assignment.

## Build and Install
```
npm install   # install npm package dependencies
npm run build  # optional build step if using TypeScript, babel, etc.
jupyter labextension install  # install the current directory as an extension
```

## Cusomize command
Line 51 of the index.ts file contains the actual command executed. If you would like to use a different command, please replace the `echo` command with your command of choice. The current configuration send the command followed by the relative path and Coursera cookie as arguements.
