"""
``django_futures.audit.py``

``autit.py`` -- Request and Task Auditing
===============================================

*TODO*

Enable auditing of tasks and requests.

* track what tasks/requests run
* track when tasks/requests run
* track all HttpClient ops
* Support DB datastore
* Support log file/journal datastore
* Support remote datastore (HTTP, ZeroMQ, AMQP, etc.)
* allow for realtime and delayed group commits to local datastore
* allow for realtime and delayed group messaging to a remote store
    * Realtime being every audit message is commited as it's created.
    * Delayed/grouped allowing multiple audit messages to be commited at once after a given period of time.
"""
