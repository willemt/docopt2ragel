#include <stdio.h>
#include <string.h>

#define BUFLEN 1024
#define BUFSIZE 2048

typedef struct
{
    /* commands */
    $command_fields

    /* flags */
    $flag_fields

    /* options */
    $option_fields

    /* arguments */
    $argument_fields

} options_t;

struct params
{
    options_t* opt;
    char buffer[BUFLEN + 1];
    int buflen;
    int cs;
};

%%{
    machine params;
    access fsm->;

    action append {
        if (fsm->buflen < BUFLEN)
            fsm->buffer[fsm->buflen++] = fc;
    }

    action term {
        if (fsm->buflen < BUFLEN)
            fsm->buffer[fsm->buflen++] = 0;
    }

    action clear { fsm->buflen = 0; }

    $command_actions
    $flag_actions
    $option_actions
    $argument_actions

    string = [^\0] + > clear $append % term;

    main := $fsm;
}%%

%% write data;

static void params_init(struct params *fsm, options_t* opt)
{
    memset(opt, 0, sizeof(options_t));

    fsm->opt = opt;
    fsm->buflen = 0;
    $option_defaults

    %% write init;
}

static void params_execute(struct params *fsm, const char *data, int len)
{
    const char *p = data;
    const char *pe = data + len;

    %% write exec;
}

static int params_finish(struct params *fsm)
{
    if (fsm->cs == params_error)
        return -1;
    if (fsm->cs >= params_first_final)
        return 1;
    return 0;
}

static void show_usage()
{
    $usage
}

static int parse_options(int argc, char **argv, options_t* options)
{
    int a;
    struct params params;

    params_init(&params, options);
    for (a = 1; a < argc; a++ )
        params_execute(&params, argv[a], strlen(argv[a]) + 1);
    if (params_finish(&params) != 1)
    {
        fprintf(stderr, "Error processing arguments\n");
        show_usage();
        return -1;
    }

    return 0;
}
