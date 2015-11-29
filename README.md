Checkouts 2.0
=============
A rewrite of the MathSOC checkouts system. Less PHP, more features. Why?
Because PHP is ugly, and we have a chance to make the API better, faster,
and easier to maintain or add features to. As well, we can rewrite the
frontend to make use of newer Javascript libraries to provide a cleaner
and smoother interface.

## Endpoints

Most requests are satisfied through a series of `GET` and `POST` endpoints
that return HTML responses.  However, there is one endpoint that supports
a JSON request.  That endpoint is used for suggestions.

### `search` endpoint

- Supported query fields:
  - `q=term` - Search term to look for.
  - `resource=resource` - One of `{assets, users}`, specifies the resource
    to search.
- Returns:

  ```
  {
    items: [
      {
        name: String name to represent object
        _id: Unique identifier (Positive Integer)
      }
    ]
  }
  ```

## Features

- Asset Management
  - Create, update, and remove assets.
  - Keep track of tock.
- User Management
  - Create, update, and remove users.
  - Keep track of users who have refunded their Mathsoc fee.
  - User profiles.
  - Different membership types: clubs, WatsFic or general (MathSoc).
- Checkouts System
  - Create, and remove checkouts.
  - Link checkouts to particular users.
  - Keep track of when an item has been checked out, to whom, and
    when it has returned.
  - See returned items and currently checked out items.

## Roadmap

- Filter checkouts by term.
- Trends
  - Most checked out item.
  - Average time item has been checked out.
  - Popular items.
- Packaging script for offline deployment.

## Development

To develop for the project, follow the following steps.  First make sure
that you have [Python installed](https://www.python.org/downloads/).  Any
version in the `2.7.X` range will work.  Then do the following in an
open terminal.

```
# Clone the project.
$ git clone git@github.com:MathSoc/Checkouts-v2

# Change into the project directory
$ cd Checkouts-v2

# Install the requirements
$ pip install -r requirements.xt

# Start the server
$ bin/run
```

## Maintainers

- [Ford Peprah](www.github.com/hkpeprah)
