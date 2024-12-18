# coding: utf-8
"""Riqu (Rest Interface for QUantum computing)

the cloud server with riqu interface.  # noqa: E501

OpenAPI spec version: 1.1

Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from quri_parts.riqu.rest.api_client import ApiClient


class JobApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def delete_job(self, job_id, **kwargs):  # noqa: E501
        """Delete Job  # noqa: E501.

        Delete the job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_job(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.delete_job_with_http_info(job_id, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_job_with_http_info(job_id, **kwargs)  # noqa: E501
            return data

    def delete_job_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Delete Job  # noqa: E501.

        Delete the job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_job_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["job_id"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_job" % key
                )
            params[key] = val
        del params["kwargs"]
        # verify the required parameter 'job_id' is set
        if "job_id" not in params or params["job_id"] is None:
            raise ValueError(
                "Missing the required parameter `job_id` when calling `delete_job`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}
        if "job_id" in params:
            path_params["job_id"] = params["job_id"]  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/jobs/{job_id}",
            "DELETE",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

    def download_file(self, job_id, **kwargs):  # noqa: E501
        """Download file  # noqa: E501.

        download file of the job.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.download_file(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.download_file_with_http_info(job_id, **kwargs)  # noqa: E501
        else:
            (data) = self.download_file_with_http_info(job_id, **kwargs)  # noqa: E501
            return data

    def download_file_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Download file  # noqa: E501.

        download file of the job.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.download_file_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["job_id"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method download_file" % key
                )
            params[key] = val
        del params["kwargs"]
        # verify the required parameter 'job_id' is set
        if "job_id" not in params or params["job_id"] is None:
            raise ValueError(
                "Missing the required parameter `job_id` when calling `download_file`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}
        if "job_id" in params:
            path_params["job_id"] = params["job_id"]  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"]
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/ssejobs/{job_id}/download-log",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type="object",  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

    def get_job(self, job_id, **kwargs):  # noqa: E501
        """Get Job  # noqa: E501.

        Get the information of the job.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: Job
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.get_job_with_http_info(job_id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_job_with_http_info(job_id, **kwargs)  # noqa: E501
            return data

    def get_job_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Get Job  # noqa: E501.

        Get the information of the job.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_job_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: Job ID (required)
        :return: Job
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["job_id"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'" " to method get_job" % key
                )
            params[key] = val
        del params["kwargs"]
        # verify the required parameter 'job_id' is set
        if "job_id" not in params or params["job_id"] is None:
            raise ValueError(
                "Missing the required parameter `job_id` when calling `get_job`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}
        if "job_id" in params:
            path_params["job_id"] = params["job_id"]  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"]
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/jobs/{job_id}",
            "GET",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type="Job",  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

    def post_job(self, **kwargs):  # noqa: E501
        """Post Job  # noqa: E501.

        Create a new job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_job(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param JobsBody body:
        :return: InlineResponse201
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.post_job_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.post_job_with_http_info(**kwargs)  # noqa: E501
            return data

    def post_job_with_http_info(self, **kwargs):  # noqa: E501
        """Post Job  # noqa: E501.

        Create a new job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_job_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param JobsBody body:
        :return: InlineResponse201
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["body"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_job" % key
                )
            params[key] = val
        del params["kwargs"]

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if "body" in params:
            body_params = params["body"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"]
        )  # noqa: E501

        # HTTP header `Content-Type`
        header_params["Content-Type"] = (
            self.api_client.select_header_content_type(  # noqa: E501
                ["application/json"]
            )
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/jobs",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type="InlineResponse201",  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

    def post_ssejob(self, **kwargs):  # noqa: E501
        """Post SSE Job  # noqa: E501.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_ssejob(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str up_file:
        :param str remark:
        :param str job_type:
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.post_ssejob_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.post_ssejob_with_http_info(**kwargs)  # noqa: E501
            return data

    def post_ssejob_with_http_info(self, **kwargs):  # noqa: E501
        """Post SSE Job  # noqa: E501.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_ssejob_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str up_file:
        :param str remark:
        :param str job_type:
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["up_file", "remark", "job_type"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_ssejob" % key
                )
            params[key] = val
        del params["kwargs"]

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}
        if "up_file" in params:
            local_var_files["up_file"] = params["up_file"]  # noqa: E501
        if "remark" in params:
            form_params.append(("remark", params["remark"]))  # noqa: E501
        if "job_type" in params:
            form_params.append(("job_type", params["job_type"]))  # noqa: E501

        body_params = None
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(
            ["application/json"]
        )  # noqa: E501

        # HTTP header `Content-Type`
        header_params["Content-Type"] = (
            self.api_client.select_header_content_type(  # noqa: E501
                ["multipart/form-data"]
            )
        )  # noqa: E501

        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/ssejobs",
            "POST",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type="object",  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )

    def put_jobs_job_id_cancel(self, job_id, **kwargs):  # noqa: E501
        """Cancel Job  # noqa: E501.

        Cancel a job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.put_jobs_job_id_cancel(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs["_return_http_data_only"] = True
        if kwargs.get("async_req"):
            return self.put_jobs_job_id_cancel_with_http_info(
                job_id, **kwargs
            )  # noqa: E501
        else:
            (data) = self.put_jobs_job_id_cancel_with_http_info(
                job_id, **kwargs
            )  # noqa: E501
            return data

    def put_jobs_job_id_cancel_with_http_info(self, job_id, **kwargs):  # noqa: E501
        """Cancel Job  # noqa: E501.

        Cancel a job  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.put_jobs_job_id_cancel_with_http_info(job_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str job_id: (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ["job_id"]  # noqa: E501
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in six.iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_jobs_job_id_cancel" % key
                )
            params[key] = val
        del params["kwargs"]
        # verify the required parameter 'job_id' is set
        if "job_id" not in params or params["job_id"] is None:
            raise ValueError(
                "Missing the required parameter `job_id` when calling `put_jobs_job_id_cancel`"
            )  # noqa: E501

        collection_formats = {}

        path_params = {}
        if "job_id" in params:
            path_params["job_id"] = params["job_id"]  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ["apiKeyAuth"]  # noqa: E501

        return self.api_client.call_api(
            "/jobs/{job_id}/cancel",
            "PUT",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )
