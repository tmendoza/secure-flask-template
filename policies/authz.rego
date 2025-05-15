package http.authz

# default deny
default allow = false

# Allow read (GET) on /v1/todos and /v1/todos/{id} for any “user” or “admin”
allow {
    input.method == "GET"
    (input.path == ["v1","todos"]      # list
     or count(input.path) == 3)         # item
    some role
    role == "user"                       # or admin
    input.token.realm_access.roles[_] == role
}

# Allow create (POST /v1/todos) for “user” or “admin”
allow {
    input.method == "POST"
    input.path == ["v1","todos"]
    some role
    role == "user"
    input.token.realm_access.roles[_] == role
}

# Allow update (PATCH) on a specific todo only to “admin”
allow {
    input.method == "PATCH"
    count(input.path) == 3
    input.path[0] == "v1"
    input.path[1] == "todos"
    input.token.realm_access.roles[_] == "admin"
}

# Allow delete (DELETE) on a specific todo only to “admin”
allow {
    input.method == "DELETE"
    count(input.path) == 3
    input.path[0] == "v1"
    input.path[1] == "todos"
    input.token.realm_access.roles[_] == "admin"
}
