let selected_course;
let selected_topic;
let coursesdict;
let selected;
let menu;

async function refreshCourses() {
  show("#loader");

  // Hide all the other "new" buttons
  hide("#addtopic");
  hide("#addelement");

  // When courses are loaded, every list should be empty
  $("#courses").empty();
  $("#topics").empty();
  $("#elements").empty();
  coursesdict = await pywebview.api.list_courses();

  // List the courses that the user owns first
  for (const course_id of coursesdict.message["rw"]) {
    course_name = await pywebview.api.get_course_attributes({
      course_id: course_id
    });
    let button = createButtonRW(course_id, course_name.message.name, function () {
      refreshTopics(course_id, "rw");
    });
    $("#courses").append(button);
  }

  // Then, list all the courses the user is subscribed to
  for (const course_id of coursesdict.message["r"]) {
    course_name = await pywebview.api.get_course_attributes({
      course_id: course_id
    });
    let button = createButtonR(course_id, course_name.message.name, function () {
      refreshTopics(course_id, "r");
    });
    $("#courses").append(button);
  }
  hide("#loader");
}

async function refreshTopics(course_id, mode) {
  show("#loader");

  // Remove and apply the gradient from the old button to the new one to make it "selected"
  $("#" + selected_course).removeClass("blue-gradient text-white");
  selected_course = course_id;
  $("#" + selected_course).addClass("blue-gradient text-white");

  // When a course is selected, we should empty the lists
  $("#topics").empty();
  $("#elements").empty();

  // Hide the new element button, and show the new topic button only if the user is authorized
  hide("#addelement");
  if (mode == "rw") {
    show("#addtopic");
  } else {
    hide("#addtopic");
  }

  topicsdict = await pywebview.api.list_topics({
    course_id: course_id
  });

  if (mode == "r") {
    // If the course is not owned by the user, create read-only buttons
    for (const topic_id of topicsdict.message) {
      topic_name = await pywebview.api.get_topic_attributes({
        topic_id: topic_id,
        course_id: course_id
      });
      let button = createButtonR(topic_id, topic_name.message.name, function () {
        refreshElements(topic_id, course_id, mode);
      })
      $("#topics").append(button);
    }
  } else {
    // If the course is owned by the user, then create read-write buttons
    for (const topic_id of topicsdict.message) {
      topic_name = await pywebview.api.get_topic_attributes({
        topic_id: topic_id,
        course_id: course_id
      });
      let button = createButtonRW(topic_id, topic_name.message.name, function () {
        refreshElements(topic_id, course_id, mode);
      })
      $("#topics").append(button);
    }
  }
  hide("#loader");
}

async function refreshElements(topic_id, course_id, mode) {
  show("#loader");

  // Remove and apply the gradient from the old button to the new one to make it "selected"
  $("#" + selected_topic).removeClass("blue-gradient text-white");
  selected_topic = topic_id;
  $("#" + selected_topic).addClass("blue-gradient text-white");

  // Before loading new elements, the element list should be emptied
  $("#elements").empty();

  // Show the new element button only if the course is owned by the user
  if (mode == "rw") {
    show("#addelement");
  } else {
    hide("#addelement");
  }

  elementsdict = await pywebview.api.list_elements({
    topic_id: topic_id,
    course_id: course_id
  });

  let button;

  if (mode == "r") {
    for (const element_id of elementsdict.message) {
      element_properties = await pywebview.api.get_element_attributes({
        element_id: element_id,
        topic_id: topic_id,
        course_id: course_id
      });
      if (element_properties.message.type == "lesson") {
        button = createButtonR(element_id, element_properties.message.name, function () {
          loadLesson(element_id, topic_id, course_id);
        })
      } else {
        button = createButtonR(element_id, element_properties.message.name, function () {
          loadQuiz(element_id, topic_id, course_id);
        })
      }
      $("#elements").append(button);
    }
  } else {
    for (const element_id of elementsdict.message) {
      element_properties = await pywebview.api.get_element_attributes({
        element_id: element_id,
        topic_id: topic_id,
        course_id: course_id
      });
      if (element_properties.message.type == "lesson") {
        button = createButtonRW(element_id, element_properties.message.name, function () {
          loadLesson(element_id, topic_id, course_id);
        })
      } else {
        button = createButtonRW(element_id, element_properties.message.name, function () {
          loadQuiz(element_id, topic_id, course_id);
        })
      }
      $("#elements").append(button);
    }
  }
  hide("#loader");
}

function createButtonRW(id, name, onclick) {
  let button = document.createElement("button");
  button.className += " btn btn-indigo btn-lg btn-block waves-effect m-1 p-4";
  button.innerHTML = name;
  button.id = id;
  button.onclick = onclick;
  return button;
}

function createButtonR(id, name, onclick) {
  let button = document.createElement("button");
  button.className += " btn btn-blue-grey btn-lg btn-block waves-effect m-1 p-4";
  button.id = id;
  button.innerHTML = name;
  button.onclick = onclick;
  return button;
}

async function loadLesson(element_id, topic_id, course_id) {
  show("#loader");
  $("#quiz-div").empty();
  selected_element_html = await pywebview.api.load_lesson_html({
    element_id: element_id,
    topic_id: topic_id,
    course_id: course_id
  });
  $(".ql-editor").html(selected_element_html.message);
  quill.disable();
  $(".ql-toolbar").hide();
  $("#edit-btn").hide();
  $("#content-editor").show();
  hide("#loader");
  toggleMain();
}

async function loadQuiz(element_id, topic_id, course_id) {
  show("#loader");
  $("#quiz-div").empty();

  $("#send-quiz-btn").click(function () {
    submitQuiz(element_id, topic_id, course_id);
  })

  let questions = await pywebview.api.get_quiz_json({
    element_id: element_id,
    topic_id: topic_id,
    course_id: course_id,
  });

  for (const [key, value] of Object.entries(questions.message)) {
    let container = document.createElement('div');
    container.classList += 'container border-top pt-3'
    container.id = key;

    let question_text = document.createElement('h4');
    question_text.innerHTML = value["text"]
    question_text.classList += "mb-3"
    container.appendChild(question_text);

    let answers = document.createElement('div')
    answers.classList += " mb-3"

    let answers_array;

    switch (value["type"]) {
      case "checkbox":
        answers.classList += " form-check"
        container.setAttribute('data-type', 'checkbox');
        answers_array = shuffle(value["wrong_answers"].concat(value["correct_answers"]))
        for (const value of answers_array) {
          answers.innerHTML = '<input class="form-check-input" type="checkbox"><label class="form-check-label">' + value + '</label>'
          container.appendChild(answers.cloneNode(true));
        }
        break;
      case "radio":
        answers.classList += " form-check"
        container.setAttribute('data-type', 'radio');
        answers_array = shuffle(value["wrong_answers"].concat([value["correct_answer"]]));
        for (const value of answers_array) {
          answers.innerHTML = '<input class="form-check-input" name="' + key + '" type="radio"><label class="form-check-label">' + value + '</label>'
          container.appendChild(answers.cloneNode(true));
        }
        break;
      case "open":
        answers.classList += " form-group"
        container.setAttribute('data-type', 'open');
        answers.innerHTML = '<input type="text" class="form-control" placeholder="Answer">'
        container.appendChild(answers.cloneNode(true));
        break;

      default:
        break;
    }
    $("#quiz-div").append(container.cloneNode(true))
  }

  toggleMain("#quiz-overlay");
  hide("#loader");
}

async function submitQuiz(element_id, topic_id, course_id) {
  let given_answers = {}
  $('#quiz-div').children().each(function () {
    let question_id = $(this).attr('id')
    switch ($(this).data("type")) {
      case "checkbox":
        given_answers[question_id] = [];
        $(this).find("input:checked").each(function () {
          given_answers[question_id].push($(this).next().text());
        });
        break;
      case "radio":
        given_answers[question_id] = ""
        $(this).find("input:checked").each(function () {
          given_answers[question_id] = $(this).next().text();
        });
        break;
      case "open":
        $(this).find("input").each(function () {
          given_answers[question_id] = $(this).val();
        });
        break;
    }
  });
  await pywebview.api.submit_quiz({
    element_id: element_id,
    topic_id: topic_id,
    course_id: course_id,
    answers: given_answers
  });
}

async function editLesson() {
  show("#loader");
  await pywebview.api.edit_lesson({
    element_id: selected,
    topic_id: selected_topic,
    course_id: selected_course,
    element_html: quill.root.innerHTML
  });
  toggleOverlay();
  hide("#loader");
}

function toggleMain(overlay = "#lesson-overlay") {
  $("#main").fadeToggle("slow", function () {
    $(overlay).fadeToggle("fast");
  });
}

function toggleOverlay(overlay = "#lesson-overlay", resetTitle = true) {
  if (resetTitle)
    pywebview.api.set_title({
      title: "Lezioni alla pari"
    });

  $(overlay).fadeToggle("slow", function () {
    $("#main").fadeToggle("fast");
  });
}

function show(id) {
  $(id).removeClass("hide");
}

function hide(id) {
  $(id).addClass("hide");
}

function addMenuListeners() {
  $("#dynamic-list").bind("contextmenu", function (ev) {
    ev.preventDefault();

    if (!["courses", "topics", "elements"].includes(ev.target.parentElement.id))
      return;
    if (
      ev.target.parentElement.id == "courses" &&
      coursesdict.message["r"].includes(ev.target.id)
    )
      return;
    if (
      ev.target.parentElement.id != "courses" &&
      coursesdict.message["r"].includes(selected_course)
    )
      return;

    selected = ev.target.id;
    $(".menu").css("top", ev.clientY - 20);
    $(".menu").css("left", ev.clientX - 20);
    $(".menu").addClass("menu-on");
    switch (ev.target.parentElement.id) {
      case "courses":
        show("#menu-course");
        hide("#menu-topic");
        hide("#menu-element");
        break;
      case "topics":
        hide("#menu-course");
        show("#menu-topic");
        hide("#menu-element");
        break;
      case "elements":
        hide("#menu-course");
        hide("#menu-topic");
        show("#menu-element");
        break;
    }
  });

  $(document).mouseup(function (e) {
    if (!$(".menu").is(e.target) && $(".menu").has(e.target).length === 0) {
      $(".menu").removeClass("menu-on");
    }
  });

  $("#mod-element").click(async function () {
    $(".menu").removeClass("menu-on");
    show("#loader");
    selected_element_html = await pywebview.api.load_lesson_html({
      element_id: selected,
      topic_id: selected_topic,
      course_id: selected_course
    });
    $(".ql-editor").html(selected_element_html.message);
    quill.enable();
    $(".ql-toolbar").show();
    $("#edit-lesson-btn").show();
    hide("#loader");
    toggleMain();
  });

  $("#del-course").click(function () {
    $("#confirm-type").val("del-course");
  });

  $("#del-topic").click(function () {
    $("#confirm-type").val("del-topic");
  });

  $("#del-element").click(function () {
    $("#confirm-type").val("del-element");
  });
}

$(window).on("load", function () {
  show("#loader");
  // Polling System for ensuring Pywebview is loaded
  let pywebview_loaded = false;
  for (let i = 0; i < 20 && !pywebview_loaded; i++) {
    setTimeout(function () {
      if (window.pywebview && !pywebview_loaded) {
        refreshCourses();
        pywebview_loaded = true;
      }
      if (i == 20) {
        alert("Si è verificato un errore.");
        throw new Error("This is for sure an Error.");
      }
    }, 100);
  }

  addMenuListeners();
  hide("#loader");
});

// Overlay button events

$("#back-lesson-btn").click(function () {
  toggleOverlay()
})
$("#edit-lesson-btn").click(function () {
  editLesson()
})
$("#back-quiz-btn").click(function () {
  toggleOverlay("#quiz-overlay")
});


// Functions for creation modal

$("#creation-modal").on("show.bs.modal", function (event) {
  var button = $(event.relatedTarget);
  var creation_type = button.data("type");
  $("#modal-title").html("Create New " + creation_type);
  $("#modal-label").html(creation_type + " Name:");
  $("#modal-submit").html("Create New " + creation_type);
  $("#modal-data-type").val(creation_type);
});

$("#creation-modal").on("hide.bs.modal", function () {
  $("#modal-name").val("");
});

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
        if (result.trim().length > 0) {
          refreshCourses();
        } else {
          alert("Si è verificato un errore durante la creazione del corso");
        }
        $("#creation-modal").modal("toggle");
        break;

      case "Topic":
        params["topic_name"] = input_text_val;
        params["course_id"] = selected_course;
        result = await pywebview.api.add_topic(params);
        if (result.trim().length > 0) {
          refreshTopics(selected_course, "rw");
        } else {
          alert("Si è verificato un errore durante la creazione del topic");
        }
        $("#creation-modal").modal("toggle");
        break;

      case "Element":
        params["element_name"] = input_text_val;
        params["topic_id"] = selected_topic;
        params["course_id"] = selected_course;
        result = await pywebview.api.add_lesson(params);
        if (result.trim().length > 0) {
          refreshElements(selected_topic, selected_course, "rw");
        } else {
          alert("Si è verificato un errore durante la creazione del topic");
        }
        $("#creation-modal").modal("toggle");
        break;

      default:
        alert("Coming soon!");
    }
  }
});

// Functions for confirmation modal

$("#confirm.modal").on("show.bs.modal", function (event) {
  $("#modal-data-type").val(button.data("type"));
});

$("#confirm-submit").click(async function () {
  let params = {};
  let result;
  switch ($("#confirm-type").val()) {
    case "del-course":
      result = await pywebview.api.remove_course(selected);
      if (result.trim().length > 0) {
        refreshCourses();
        $("#confirm-modal").modal("toggle");
      } else {
        alert("Si è verificato un errore durante l'eliminazione del corso");
      }
      break;
    case "del-topic":
      params["course_id"] = selected_course;
      params["topic_id"] = selected;
      result = await pywebview.api.remove_topic(params);
      if (result.trim().length > 0) {
        refreshTopics(selected_course, "rw");
        $("#confirm-modal").modal("toggle");
      } else {
        alert("Si è verificato un errore durante l'eliminazione del topic");
      }
      break;
    case "del-element":
      params["course_id"] = selected_course;
      params["topic_id"] = selected_topic;
      params["element_id"] = selected;
      result = await pywebview.api.remove_element(params);
      if (result.trim().length > 0) {
        refreshElements(selected_topic, selected_course, "rw");
        $("#confirm-modal").modal("toggle");
      } else {
        alert("Si è verificato un errore durante l'eliminazione dell'elemento");
      }
      break;
    default:
      alert("Wait, this wasn't supposed to happen!");
      break;
  }
});

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}