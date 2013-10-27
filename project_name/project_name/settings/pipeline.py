STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'base': {
        'source_filenames': (
            'css/bootstrap.min.css',
            'css/bootstrap-theme.min.css',
        ),
        'output_filename': 'css/base.css',
    },
}

PIPELINE_JS = {
    'jquery': {
        'source_filenames': (
            'js/jquery-1.10.2.min.js',
        ),
        'output_filename': 'js/jquery.js'
    },
    'base': {
        'source_filenames': (
            'js/bootstrap.min.js',
        ),
        'output_filename': 'js/base.js',
    },
}

PIPELINE_DISABLE_WRAPPER = True