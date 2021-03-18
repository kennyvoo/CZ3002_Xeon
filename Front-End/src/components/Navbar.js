import React from "react";
import {
  Pane,
  Text,
  Button,
  Heading,
  ListIcon,
  IconButton,
  SideSheet,
  Paragraph,
  Avatar,
  WarningSignIcon,
  Popover,
  Menu,
  Position,
  toaster,
  PeopleIcon,
  CircleArrowRightIcon,
  EditIcon,
  TrashIcon,
  SmallCrossIcon,
  UndoIcon,
  TimeIcon,
  AsteriskIcon
} from "evergreen-ui";
import { Link } from "react-router-dom";
import { IoLibraryOutline } from "react-icons/io5";

function Navbar() {
  var accName = "Hou Jing";

  return (
    <Pane display="flex" padding={0} background="grey" borderRadius={0}>
      <Pane flex={1} alignItems="center" display="flex" paddingLeft={7}>
        {/* <IconButton icon={ListIcon} margin={10} appearance="default" /> */}
        <IoLibraryOutline size={30} color="white" />
        <Link to="/" style={{ textDecoration: "none" }}>
          <Heading marginRight={5} marginLeft={5} size={700} color="white">
            SmartLib
          </Heading>
        </Link>
      </Pane>
      <Pane backgroundColor="none">
        {/* <Link to="/MyBookings" style={{ textDecoration: "none" }}>
          <Button margin={8}>My Bookings</Button>
        </Link>
        <Link to="/Account" style={{ textDecoration: "none" }}>
          <Button margin={8}>My Account</Button>
        </Link> */}
        <Link to="/Login" style={{ textDecoration: "none" }}>
          <Button margin={8} appearance="primary" intent="success">
            Login
          </Button>
        </Link>
        {/* <Link to="/CreateAccount" style={{ textDecoration: "none" }}>
          <Button margin={8} appearance="primary">
            Create Account
          </Button>
        </Link> */}
        <Popover
          position={Position.BOTTOM_LEFT}
          content={
            <Menu>
              <Menu.Group>
                <Link to="/MyBookings" style={{ textDecoration: "none" }}>
                  <Menu.Item icon={TimeIcon}>My Bookings</Menu.Item>
                </Link>
                <Link to="/Account" style={{ textDecoration: "none" }}>
                  <Menu.Item icon={PeopleIcon}>Account Settings</Menu.Item>
                </Link>
                <Link to="/Admin" style={{ textDecoration: "none" }}>
                  <Menu.Item icon={AsteriskIcon}>Admin Home Page</Menu.Item>
                </Link>
                <Link to="/ModifySeats" style={{ textDecoration: "none" }}>
                  <Menu.Item icon={AsteriskIcon}>Modify Seats</Menu.Item>
                </Link>
                <Link to="/AddSeats" style={{ textDecoration: "none" }}>
                  <Menu.Item icon={AsteriskIcon}>Add New Seat</Menu.Item>
                </Link>
              </Menu.Group>
              <Menu.Divider />
              <Menu.Group>
                <Menu.Item icon={UndoIcon} intent="danger">
                  Sign Out
                </Menu.Item>
              </Menu.Group>
            </Menu>
          }
        >
          <Button>My Acc</Button>
        </Popover>
      </Pane>
      <Avatar name={accName} size={30} margin={8} />
    </Pane>
  );
}

function MyBookingButton() {
  return (
    <Button margin={8}>My Bookings</Button>
  );
}

function MyAccountButton() {
  return (
    <Button margin={8}>My Account</Button>
  );
}

function CreateAccountButton() {
  return (
    <Button margin={8} appearance="primary">
      Create Account
    </Button>
  );
}

function UserAvatar() {
  return (
    <Avatar name="Hou Jing" size={30} margin={8} />
  );
}

export default Navbar;

