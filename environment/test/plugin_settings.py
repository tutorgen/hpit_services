class PluginSettings:
    DATASHOP_ROOT_URL = "https://pslcdatashop.web.cmu.edu/services"
    DATASHOP_SERVICES_URL = "http://pslc-qa.andrew.cmu.edu/datashop/services"
    MONGODB_URI = 'mongodb://localhost:27017/'
    #COUCHBASE_HOSTNAME = "127.0.0.1"
    #COUCHBASE_BUCKET_URI = "http://127.0.0.1:8091/pools/default/buckets"
    COUCHBASE_HOSTNAME = "beta.hpit-project.org"
    COUCHBASE_BUCKET_URI = "http://beta.hpit-project.org:8091/pools/default/buckets"
    COUCHBASE_USERNAME = "Administrator"
    COUCHBASE_PASSWORD = "Administrator"
    COUCHBASE_AUTH = (COUCHBASE_USERNAME, COUCHBASE_PASSWORD)
