from golang:1-alpine
workdir /app
copy hello.go hello.go
run go build hello.go
expose 8081
entrypoint ["./hello"] # this produces a large image
