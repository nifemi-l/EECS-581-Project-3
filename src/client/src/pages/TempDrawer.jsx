// Prologue
// Name: TempDrawer.jsx
// Description: Create a reusable "temporary drawer" using the react mui library. This will be used to navigate between pages.
// Programmer: Blake Carlson
// Creation date: 11/09/25
// Last revision date: 11/09/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled appropriately.

import React from "react";
import { Drawer, Toolbar, IconButton, Divider, List, ListItem, ListItemText } from "@mui/material";
import { Link } from "react-router-dom";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";

const drawerWidth = 150;

export default function TempDrawer({ open, onClose }) {

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
        },
      }}
    >
      <Toolbar>
        <IconButton onClick={onClose}>
          <ChevronLeftIcon />
        </IconButton>
      </Toolbar>
      <Divider />
      <List>
        {[
          { text: "Dashboard", path: "/dashboard" },
          { text: "Leaderboard", path: "/leaderboard" },
          { text: "About", path: "/about" },
        ].map((item) => (
          <ListItem button key={item.text} component={Link} to={item.path} onClick={onClose}>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}