#include <stdio.h>
#include <string.h>
#include <libgen.h>
#include <stdlib.h>
#include <wchar.h>
#include "Python.h"

/**
 * A small note on encoding: This does as much as it can in UTF-8 mode,
 * with the only work done with wchar_t being to test for the actual
 * existence of files on windows.
 */

void init_librenpy(void);

#define EXPORT

#undef DEBUG_EXISTS

/* The name of the directory containing the exe. */
static char *exedir;

/* The name of the .py file to use */
static char *pyname;

/**
 * The Python config object.
 */
PyConfig config;

/**
 * Returns true if every character in a is equivalent to the characters in b0 or b1,
 * and the strings are of the same length. (This exists because strcasecmp considers
 * locale, and we don't want that.)
 */
static int compare(const char *a, const char *b0, const char *b1) {
    while (1) {
        if (*a != *b0 && *a != *b1) {
            return 0;
        }

        if (!*a) {
            return 1;
        }

        a += 1;
        b0 += 1;
        b1 += 1;
    }
}


/**
 * This takes argv0 and sets the exedir and pyname variables.
 */
static void take_argv0(char *argv0) {

    config.program_name = Py_DecodeLocale(argv0, NULL);

    // This copy is required because dirname can change its arguments.
    argv0 = strdup(argv0);

    // Basename. This seems to be broken in certain locales, so it's
    // reimplemented here.
    char *exename = argv0 + strlen(argv0) -1;
    while (exename > argv0) {
        if (*exename == '\\' || *exename == '/') {
            *exename = 0;
            exename += 1;
            break;
        }
        exename -= 1;
    }

    int pyname_size = strlen(exename) + strlen(".py") + 1;

    pyname = (char *) malloc(pyname_size);
    strncpy(pyname, exename, pyname_size);

    strncat(pyname, ".py", pyname_size);

    exedir = strdup(argv0);
    if (exename == argv0) {
        exedir = strdup(".");
    } else {
        exedir = strdup(argv0);
    }

    free(argv0);
}

/**
 * This combines the exedir and up to two components, and returns the result.
 * It returns a newly allocated string.
 */
static char *join(const char *p1, const char *p2) {
    int size = strlen(exedir) + 1;

    if (p1) {
        size += strlen(p1);
    }

    if (p2) {
        size += strlen(p2);
    }

    char *rv = (char *) malloc(size);

    strncpy(rv, exedir, size);

    if (p1) {
        strncat(rv, p1, size);
    }

    if (p2) {
        strncat(rv, p2, size);
    }

    return rv;
}

/*
 * This combines exedir with the optional p1 and p2. It returns 1 if the
 * file exists, and 0 otherwise.
 */
static int exists(const char *p1, const char *p2) {
    char *path = join(p1, p2);

    FILE *f = fopen(path, "rb");

#ifdef DEBUG_EXISTS
    printf("%s", path);
#endif

    free(path);

    if (f) {
        fclose(f);

#ifdef DEBUG_EXISTS
        printf(" exists.\n");
#endif

        return 1;
    } else {
#ifdef DEBUG_EXISTS
        printf(" does not exist.\n");
#endif

        return 0;
    }
}

/**
 * This tries to find a python home in p. If one hasn't been found already,
 * it calls Py_SetPythonHome.
 */
static void find_python_home(const char *p) {
    static int found = 0;

    if (found) {
        return;
    }

    if (exists(p, "/lib/" PYTHONVER "/site.pyc") ||
        exists(p, "/lib/python" PYCVER ".zip")) {

        found = 1;
        config.home = Py_DecodeLocale(join(p, NULL), NULL);
        config.prefix = config.home;
        config.exec_prefix = config.home;
        PyWideStringList_Append(&config.module_search_paths, Py_DecodeLocale(join(p, "/lib/" PYTHONVER), NULL));
        PyWideStringList_Append(&config.module_search_paths, Py_DecodeLocale(join(p, "/lib/python" PYCVER ".zip"), NULL));
        config.module_search_paths_set = 1;
    }
}

/**
 * Searches for the python home directory in the platform-specific location.
 */
static void search_python_home(void) {

    // Relative to the base directory.
    find_python_home("");

    // Relative to lib/freebsd-x86_64.
    find_python_home("/../..");

}


/**
 * This finds the main python file. If it's been found, sets pyname to the
 * value that's been found.
 */
static void find_pyname(const char *p) {
    static int found = 0;

    if (found) {
        return;
    }

    if (exists(p, pyname)) {
        found = 1;
        pyname = join(p, pyname);
        return;
    }

    if (exists(p, "main.py")) {
        found = 1;
        pyname = join(p, "main.py");
        return;
    }
}


static void search_pyname() {

    // Relative to the base directory.
    find_pyname("/");

    // Relative to lib/freebsd-x86_64
    find_pyname("/../../");

}

/**
 * This sets the RENPY_PLATFORM environment variable, if it hasn't been set
 * already.
 */
static void set_renpy_platform() {
    if (!getenv("RENPY_PLATFORM")) {
        putenv("RENPY_PLATFORM=" PLATFORM "-" ARCH);
    }
}

/**
 * Preinitializes Python, to enable UTF-8 mode.
 */

static void preinitialize(int isolated, int argc, char **argv) {
    PyPreConfig preconfig;

    // Initialize PreConfig.
    if (isolated) {
        PyPreConfig_InitIsolatedConfig(&preconfig);
    } else {
        PyPreConfig_InitPythonConfig(&preconfig);
    }

    preconfig.utf8_mode = 1;
    preconfig.use_environment = 0;

    Py_PreInitializeFromBytesArgs(&preconfig, argc, argv);

    init_librenpy();

    // Initialize Config.
    if (isolated) {
        PyConfig_InitIsolatedConfig(&config);
    } else {
        PyConfig_InitPythonConfig(&config);
    }

}

/**
 * The same, but use wchar_t arguments.
 */
static void preinitialize_wide(int isolated, int argc, wchar_t **argv) {
    PyPreConfig preconfig;

    // Initialize PreConfig.
    if (isolated) {
        PyPreConfig_InitIsolatedConfig(&preconfig);
    } else {
        PyPreConfig_InitPythonConfig(&preconfig);
    }

    preconfig.utf8_mode = 1;
    preconfig.use_environment = 0;

    Py_PreInitializeFromArgs(&preconfig, argc, argv);

    init_librenpy();

    // Initialize Config.
    if (isolated) {
        PyConfig_InitIsolatedConfig(&config);
    } else {
        PyConfig_InitPythonConfig(&config);
    }

}


/**
 * This is the python command, and all it does is to modify the path to the
 * python library, and start python.
 */
int EXPORT renpython_main(int argc, char **argv) {

    preinitialize(0, argc, argv);

    set_renpy_platform();
    take_argv0(argv[0]);
    search_python_home();

    config.user_site_directory = 0;
    Py_InitializeFromConfig(&config);

    return Py_BytesMain(argc, argv);
}

int EXPORT renpython_main_wide(int argc, wchar_t **argv) {

    preinitialize_wide(0, argc, argv);

    set_renpy_platform();
    take_argv0(Py_EncodeLocale(argv[0], NULL));
    search_python_home();

    config.user_site_directory = 0;
    Py_InitializeFromConfig(&config);

    return Py_Main(argc, argv);
}


/**
 * This is called from the launcher executable, to start Ren'Py running.
 */
int EXPORT launcher_main(int argc, char **argv) {

    preinitialize(1, argc, argv);

    set_renpy_platform();
    take_argv0(argv[0]);
    search_python_home();

    config.user_site_directory = 0;
    config.parse_argv = 1;
    config.install_signal_handlers = 1;

    search_pyname();

    // Figure out argv.
    char **new_argv = (char **) alloca((argc + 1) * sizeof(char *));

    new_argv[0] = argv[0];
    new_argv[1] = pyname;

    for (int i = 1; i < argc; i++) {
        new_argv[i + 1] = argv[i];
    }

    PyConfig_SetBytesArgv(&config, argc + 1, new_argv);
    Py_InitializeFromConfig(&config);

    return Py_RunMain();
}

/**
 * This is called from the launcher executable, to start Ren'Py running.
 */
int EXPORT launcher_main_wide(int argc, wchar_t **argv) {

    preinitialize_wide(1, argc, argv);

    set_renpy_platform();
    take_argv0(Py_EncodeLocale(argv[0], NULL));
    search_python_home();

    config.user_site_directory = 0;
    config.parse_argv = 1;
    config.install_signal_handlers = 1;

    search_pyname();

    // Figure out argv.
    wchar_t **new_argv = (wchar_t **) alloca((argc + 1) * sizeof(wchar_t *));

    new_argv[0] = argv[0];
    new_argv[1] = Py_DecodeLocale(pyname, NULL);

    for (int i = 1; i < argc; i++) {
        new_argv[i + 1] = argv[i];
    }

    PyConfig_SetArgv(&config, argc + 1, new_argv);
    Py_InitializeFromConfig(&config);

    return Py_RunMain();
}
