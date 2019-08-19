let selected_course
let selected_topic

async function refreshCourses() {
    show('#loader');

    hide("#addtopic");
    hide("#addelement");

    $("#courses").empty();
    $("#topics").empty();
    $("#elements").empty();
    coursesdict = await pywebview.api.list_courses()

    for (const course_id of coursesdict.message["rw"]) {
        let button = document.createElement("button");
        button.className += " btn btn-indigo btn-lg btn-block waves-effect m-1 p-4";
        button.id = course_id;
        course_name = await pywebview.api.get_course_attributes({
            "course_id": course_id
        })
        button.innerHTML = course_name.message.name
        button.onclick = function () {
            refreshTopics(course_id, "rw")
        }
        $("#courses").append(button);
    };
    for (const course_id of coursesdict.message["r"]) {
        let button = document.createElement("button");
        button.className += " btn btn-blue-grey btn-lg btn-block waves-effect m-1 p-4";
        button.id = course_id;
        course_name = await pywebview.api.get_course_attributes({
            "course_id": course_id
        })
        button.innerHTML = course_name.message.name
        button.onclick = function () {
            refreshTopics(course_id, "r")
        }
        $("#courses").append(button);
    };
    hide('#loader');
}

async function refreshTopics(course_id, mode) {
    show('#loader');

    $("#" + selected_course).removeClass("blue-gradient text-white")
    selected_course = course_id;
    $("#" + selected_course).addClass("blue-gradient text-white")

    $("#topics").empty();
    $("#elements").empty();

    if (!($("#addelement").hasClass("hide"))) {
        hide("#addelement");
    }
    if (mode == "rw") {
        if ($("#addtopic").hasClass("hide")) {
            show("#addtopic")
        };
    } else {
        if (!($("#addtopic").hasClass("hide"))) {
            hide("#addtopic")
        };
    }

    topicsdict = await pywebview.api.list_topics({
        "course_id": course_id
    })
    for (const topic_id of topicsdict.message) {
        let button = document.createElement("button");
        button.className += " btn btn-lg btn-block waves-effect m-1 p-4";
        button.className += mode == "r" ? " btn-blue-grey" : " btn-indigo"
        button.id = topic_id;
        topic_name = await pywebview.api.get_topic_attributes({
            "topic_id": topic_id,
            "course_id": course_id
        });
        button.innerHTML = topic_name.message.name;
        button.onclick = function () {
            refreshElements(topic_id, course_id, mode)
        };
        $("#topics").append(button);
    };
    hide('#loader');
}

async function refreshElements(topic_id, course_id, mode) {
    show('#loader');

    $("#" + selected_topic).removeClass("blue-gradient text-white")
    selected_topic = topic_id;
    $("#" + selected_topic).addClass("blue-gradient text-white")

    $("#elements").empty();

    if (mode == "rw") {
        if ($("#addelement").hasClass("hide")) {
            show("#addelement");
        }
    } else {
        if (!($("#addelement").hasClass("hide"))) {
            hide("#addelement");
        }
    }

    elementsdict = await pywebview.api.list_elements({
        "topic_id": topic_id,
        "course_id": course_id
    });
    for (const element_id of elementsdict.message) {
        let button = document.createElement("button");
        button.className += " btn btn-lg btn-block waves-effect m-1 p-4";
        button.className += mode == "r" ? " btn-blue-grey" : " btn-indigo"
        button.id = element_id;
        element_properties = await pywebview.api.get_element_attributes({
            "element_id": element_id,
            "topic_id": topic_id,
            "course_id": course_id
        });
        button.innerHTML = element_properties.message.name;
        button.onclick = async function (element_type) {
            html_test = await pywebview.api.load_element_html({
                "element_id": element_id,
                "topic_id": topic_id,
                "course_id": course_id
            })
            $("#overlay").html(html_test.message)
            toggleMain();
        };

        $("#elements").append(button);
    };
    hide('#loader');
}

function toggleMain() {
    $("#main").fadeToggle("slow", function () {
        $("#overlay").fadeToggle("fast");
    });
}

function toggleOverlay() {
    $("#overlay").fadeToggle("slow", function () {
        $("#main").fadeToggle("fast");
    });
}

function show(id) {
    $(id).removeClass("hide")
}

function hide(id) {
    $(id).addClass("hide")
}

$(window).on('load', function () {

    show('#loader');
    let pywebview_loaded = false;
    for (let i = 0; i < 20 && !pywebview_loaded; i++) {
        setTimeout(function () {
            if (window.pywebview && !pywebview_loaded) {
                refreshCourses();
                pywebview_loaded = true;
            }
            if (i == 20) {
                alert("Si è verificato un errore.");
                throw new Error('This is for sure an Error.');
            }
        }, 100);
    }
    hide('#loader');
});

$('#creation-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget)
    var creation_type = button.data('type')
    var modal = $(this)
    $("#modal-title").html("Create New " + creation_type)
    $("#modal-label").html(creation_type + " Name:")
    $("#modal-submit").html("Create New " + creation_type)
    $("#modal-data-type").val(creation_type)
})

$('#creation-modal').on('hide.bs.modal', function (event) {
    $("#modal-name").val("");
})

$("#modal-submit").click(async function () {
    input_text_val = $("#modal-name").val();
    modal_data_type = $("#modal-data-type").val();
    if (input_text_val.trim().length > 0) {
        let params = {};
        let result;
        switch (modal_data_type) {
            case "Course":
                params["course_name"] = input_text_val;
                result = await pywebview.api.add_course(params);
                if (result.trim().length > 0)
                    refreshCourses();
                else
                    alert("Si è verificato un errore durante la creazione del corso")
                $("#creation-modal").modal("toggle");
                break;

            case "Topic":
                params["topic_name"] = input_text_val;
                params["course_id"] = selected_course;
                result = await pywebview.api.add_topic(params);
                if (result.trim().length > 0)
                    refreshTopics(selected_course, "rw");
                else
                    alert("Si è verificato un errore durante la creazione del topic")
                $("#creation-modal").modal("toggle");
                break;

            case "Element":
                params["element_name"] = input_text_val;
                params["element_type"] = "lesson";
                params["topic_id"] = selected_topic;
                params["course_id"] = selected_course;
                result = await pywebview.api.add_element(params);
                if (result.trim().length > 0)
                    refreshElements(selected_topic, selected_course, "rw");
                else
                    alert("Si è verificato un errore durante la creazione del topic")
                $("#creation-modal").modal("toggle");
                break;

            default:
                alert("Coming soon!")
        }
    }
})