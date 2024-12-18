# coding: utf-8
"""Riqu (Rest Interface for QUantum computing)

the cloud server with riqu interface.  # noqa: E501

OpenAPI spec version: 1.1

Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class JobsBody(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        "qasm": "str",
        "transpiler": "str",
        "shots": "int",
        "remark": "str",
        "job_type": "str",
    }

    attribute_map = {
        "qasm": "qasm",
        "transpiler": "transpiler",
        "shots": "shots",
        "remark": "remark",
        "job_type": "job_type",
    }

    def __init__(
        self, qasm=None, transpiler=None, shots=None, remark=None, job_type=None
    ):  # noqa: E501
        """JobsBody - a model defined in Swagger"""  # noqa: E501
        self._qasm = None
        self._transpiler = None
        self._shots = None
        self._remark = None
        self._job_type = None
        self.discriminator = None
        self.qasm = qasm
        if transpiler is not None:
            self.transpiler = transpiler
        self.shots = shots
        if remark is not None:
            self.remark = remark
        if job_type is not None:
            self.job_type = job_type

    @property
    def qasm(self):
        """Gets the qasm of this JobsBody.  # noqa: E501.

        OpenQASM program  # noqa: E501

        :return: The qasm of this JobsBody.  # noqa: E501
        :rtype: str
        """
        return self._qasm

    @qasm.setter
    def qasm(self, qasm):
        """Sets the qasm of this JobsBody.

        OpenQASM program  # noqa: E501

        :param qasm: The qasm of this JobsBody.  # noqa: E501
        :type: str
        """
        if qasm is None:
            raise ValueError(
                "Invalid value for `qasm`, must not be `None`"
            )  # noqa: E501

        self._qasm = qasm

    @property
    def transpiler(self):
        """Gets the transpiler of this JobsBody.  # noqa: E501.

        :return: The transpiler of this JobsBody.  # noqa: E501
        :rtype: str
        """
        return self._transpiler

    @transpiler.setter
    def transpiler(self, transpiler):
        """Sets the transpiler of this JobsBody.

        :param transpiler: The transpiler of this JobsBody. # noqa:
            E501
        :type: str
        """

        self._transpiler = transpiler

    @property
    def shots(self):
        """Gets the shots of this JobsBody.  # noqa: E501.

        :return: The shots of this JobsBody.  # noqa: E501
        :rtype: int
        """
        return self._shots

    @shots.setter
    def shots(self, shots):
        """Sets the shots of this JobsBody.

        :param shots: The shots of this JobsBody.  # noqa: E501
        :type: int
        """
        if shots is None:
            raise ValueError(
                "Invalid value for `shots`, must not be `None`"
            )  # noqa: E501

        self._shots = shots

    @property
    def remark(self):
        """Gets the remark of this JobsBody.  # noqa: E501.

        :return: The remark of this JobsBody.  # noqa: E501
        :rtype: str
        """
        return self._remark

    @remark.setter
    def remark(self, remark):
        """Sets the remark of this JobsBody.

        :param remark: The remark of this JobsBody.  # noqa: E501
        :type: str
        """

        self._remark = remark

    @property
    def job_type(self):
        """Gets the job_type of this JobsBody.  # noqa: E501.

        :return: The job_type of this JobsBody.  # noqa: E501
        :rtype: str
        """
        return self._job_type

    @job_type.setter
    def job_type(self, job_type):
        """Sets the job_type of this JobsBody.

        :param job_type: The job_type of this JobsBody.  # noqa: E501
        :type: str
        """

        self._job_type = job_type

    def to_dict(self):
        """Returns the model properties as a dict."""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (
                            (item[0], item[1].to_dict())
                            if hasattr(item[1], "to_dict")
                            else item
                        ),
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(JobsBody, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model."""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal."""
        if not isinstance(other, JobsBody):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal."""
        return not self == other
