# QURI Parts riqu

QURI Parts riqu is a support library for using quantum computers provided by the cloud server
with riqu (**R**EST **I**nterface for **Qu**antum Computing) interface.

This package is experimental and may undergo breaking changes without notice.
Use it at your own risk.

## Documentation

[QURI Parts Documentation](https://quri-parts.qunasys.com)

## Installation

QURI Parts requires Python 3.9.8 or later.

Use `pip` to install QURI Parts.
Default installation only contains components not depending specific platforms (devices/simulators) or external libraries.
You need to specify *extras* with square brackets (`[]`) to use those platforms and external libraries with QURI Parts:

```
# Default installation, no extras
pip install quri-parts

# Use Qulacs, a quantum circuit simulator
pip install "quri-parts[qulacs]"

# Use Amazon Braket SDK
pip install "quri-parts[braket]"

# Use Qulacs and OpenFermion, a quantum chemistry library for quantum computers
pip install "quri-parts[qulacs,openfermion]"
```

Currently available extras are as follows:

- `qulacs`
- `braket`
- `qiskit`
- `cirq`
- `openfermion`
- `stim`
- `openqasm`
- `riqu`

You can also install individual components (`quri-parts-*`) directly.
In fact, `quri-parts` is a meta package, a convenience method to install those individual components.

### Installation from local source tree

If you check out the QURI Parts repository and want to install from that local source tree, you can use `requirements-local.txt`.
In `requirements-local.txt`, optional components are commented out, so please uncomment them as necessary.

```
pip install quri-parts-riqu
pip install -r requirements-local.txt
```


## Documentation and tutorials

Documentation of QURI Parts is available at <https://quri-parts.qunasys.com>.
[Tutorials](https://quri-parts.qunasys.com/tutorials.html) would be a good starting point.

## Release notes

See [Releases page](https://github.com/QunaSys/quri-parts/releases) on GitHub.


## Contribution guidelines

If you are interested in contributing to QURI Parts, please take a look at our [contribution guidelines](CONTRIBUTING.md).


## Authors

QURI Parts developed and maintained by [QunaSys Inc.](https://qunasys.com/en). All contributors can be viewed on [GitHub](https://github.com/QunaSys/quri-parts/graphs/contributors).


## License

Apache License 2.0
