# What's New 
Converting local auth to Cloud auth

""""""
First thing first: Nuke this file before merge
- Work in progress, grep `TODO(auth)` to find out what's missing
""""""

**Frontend** 
Two level of auth, Admin & Operator. TodoL Change Auth to connect with Cloud + Guest
- Auth with Cloud
  - [x] Redo UI to add Connect via Cloud
  - [ ] Query Auth method
  - [ ] Determine the right Auth method
  - [ ] Call auth + Callback + retreive token
  - [ ] Let the user choose the right `workspace`
  - [ ] Set the permission (TBD, Cloud split permission for each Test Profile)
    - Talk with @itsjoeoui & @39bytes
  - [ ] Introduction of a env var for which Cloud to use (api URL) in the build ?
    - Talk with @itsjoeoui & @39bytes
    - We could add an image to display in studio at login for easily identify the Cloud
- Auth with Guest
  - [ ] UI to bypass auth
  - [ ] Unset the Cloud env var

**Backend**
Three level of auth
- Admin (full access)
  - [x] Already implemented
- Operator (limited access (frontend primaly, but lock some route for double protection))
  - [ ] Currently locked with `is_admin`
- Guest
  - [ ] All admin without `Cloud` access
  - [ ] Lock `*/cloud/*` route
  - [ ] Lock load profile
  - [ ] Filter env vars so guest can't get set the Cloud env var
