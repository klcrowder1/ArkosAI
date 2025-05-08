# Using the Issue Tracker

This document explains how to use the issue tracker CSV file to track progress on the Arkos AI project.

## Overview

The issue tracker (`docs/development/issue-tracker.csv`) is a simple CSV file that lists all the issues for the Arkos AI project, organized by phase and milestone. It provides a way for both developers and AI assistants to track what work has been completed and what's next.

## CSV Structure

The issue tracker CSV file has the following columns:

- **Issue ID**: A unique identifier for the issue, in the format `P<phase>-M<milestone>-<number>` (e.g., P1-M1-1)
- **Title**: The title of the issue
- **Status**: The current status of the issue (Open, In Progress, Closed)
- **Priority**: The priority of the issue (High, Medium, Low)
- **Milestone**: The milestone the issue belongs to
- **Assignee**: The person assigned to the issue
- **Related Documentation**: Links to relevant documentation
- **Dependencies**: Other issues that this issue depends on
- **Notes**: Additional notes about the issue

## How to Update the Issue Tracker

### Updating Issue Status

When you start working on an issue, update its status to "In Progress":

1. Open the `docs/development/issue-tracker.csv` file
2. Find the issue you're working on
3. Change the "Status" column from "Open" to "In Progress"
4. Save the file

When you complete an issue, update its status to "Closed":

1. Open the `docs/development/issue-tracker.csv` file
2. Find the issue you've completed
3. Change the "Status" column from "In Progress" to "Closed"
4. Save the file

### Updating Assignees

When you assign an issue to someone:

1. Open the `docs/development/issue-tracker.csv` file
2. Find the issue you want to assign
3. Add the assignee's name or username to the "Assignee" column
4. Save the file

### Adding Notes

If you want to add notes about an issue:

1. Open the `docs/development/issue-tracker.csv` file
2. Find the issue you want to add notes to
3. Add your notes to the "Notes" column
4. Save the file

## Viewing the Issue Tracker

You can view the issue tracker in several ways:

### Using a Text Editor

You can open the CSV file in any text editor to view its contents. This is the simplest method but doesn't provide a great visualization.

### Using a Spreadsheet Application

You can open the CSV file in a spreadsheet application like Microsoft Excel, Google Sheets, or LibreOffice Calc. This provides a better visualization and allows for easier editing.

### Using CSV Viewers

There are many CSV viewers available that can provide a better visualization of the data. Some options include:

- VS Code with the "Rainbow CSV" extension
- Online CSV viewers
- Command-line tools like `csvlook`

## Filtering and Sorting

When viewing the issue tracker in a spreadsheet application, you can use filtering and sorting to focus on specific issues:

### Filtering

- Filter by "Status" to see only open, in-progress, or closed issues
- Filter by "Priority" to see only high, medium, or low priority issues
- Filter by "Milestone" to see issues for a specific milestone
- Filter by "Assignee" to see issues assigned to a specific person

### Sorting

- Sort by "Issue ID" to see issues in their original order
- Sort by "Priority" to see high-priority issues first
- Sort by "Status" to group issues by their status
- Sort by "Milestone" to group issues by milestone

## Finding the Next Task

To find the next task to work on:

1. Filter the issue tracker to show only "Open" issues
2. Sort by "Priority" (descending) and "Issue ID" (ascending)
3. Check the "Dependencies" column to ensure all dependencies are closed
4. The first issue in the list that has all its dependencies closed is the next task to work on

## Updating GitHub Issues

If you're using GitHub Issues to track tasks, you should update both the CSV file and the corresponding GitHub Issue when you start or complete a task:

1. Update the status in the CSV file as described above
2. Update the GitHub Issue:
   - Add a comment indicating the status change
   - Close the issue if the task is completed
   - Add labels as appropriate

## Example Workflow

Here's an example workflow for using the issue tracker:

1. Open the issue tracker CSV file
2. Filter to show only "Open" issues
3. Sort by "Priority" and "Issue ID"
4. Identify the highest-priority issue that has all its dependencies closed
5. Assign the issue to yourself
6. Change the status to "In Progress"
7. Work on the issue
8. When completed, change the status to "Closed"
9. Add any relevant notes
10. Save the file
11. Repeat for the next issue

## For AI Assistants

AI assistants like Claude can use the issue tracker to understand the current state of the project and provide more relevant assistance:

1. Read the issue tracker CSV file to understand what issues are open, in progress, and closed
2. Use this information to prioritize tasks and provide more relevant suggestions
3. When helping with a task, reference the issue ID and title
4. Suggest updates to the issue tracker when tasks are completed

## Conclusion

The issue tracker CSV file provides a simple but effective way to track progress on the Arkos AI project. By keeping it up to date, both developers and AI assistants can stay on the same page about what work has been completed and what's next.
