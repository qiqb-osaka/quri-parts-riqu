#!/bin/sh

set -e

sphinx-apidoc -e -f --implicit-namespaces -o ./quri_parts/riqu -M ../quri_parts
