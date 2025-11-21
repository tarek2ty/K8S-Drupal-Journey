from golang:1-alpine as build
workdir /app
copy hello.go hello.go
run go build hello.go

from alpine:latest
workdir /app
copy --from=build /app/hello /app/hello

expose 8081
entrypoint ["./hello"] # this produces a significantly smaller image
