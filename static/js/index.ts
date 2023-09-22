/**
 * Entry file for the JavaScript webapp
 *
 * Functions declared as 'export function' inside modules that are 
 * exported here will be available in the HTML as `hedyApp.myFunction(...)`.
 *
 * Files that don't export any functions that are used directly from the HTML
 * should be included by using an 'import' statement.
 *
 * If you want to do any work upon loading the page (such as attaching DOM event
 * listeners), define and export an initialization function, and call that 
 * from 'initialize.ts'.
 */
import './htmx-integration';
export {
    error,
    modal,
} from './modal';

export {
    change_keyword_language,
    change_language,
    closeAchievement,
    closeContainingModal,
    confetti_cannon,
    copy_to_clipboard,
    delete_program,
    downloadSlides,
    filter_admin,
    hide_editor,
    modalStepOne,
    report_program,
    runit,
    saveMachineFiles,
    select_profile_image,
    set_explore_favourite,
    set_favourite_program,
    share_program,
    show_editor,
    showAchievements,
    showVariableView,
    submit_program,
    stopit,
    toggle_developers_mode,
    toggle_keyword_language,
    tryPaletteCode,
    viewProgramLink,
} from './app';

export {
    changeUserEmail,
    comeBackHereAfterLogin,
    destroy,
    destroy_public,
    edit_user_tags,
    markAsTeacher,
    request_teacher_account,
    update_user_tags,
    logout,
} from './auth';
export {
    InitLineChart,
    resolve_student,
    toggle_show_students_class_overview,
} from './statistics';
export {
    startLevelTutorial,
} from './tutorials/tutorial';
export {
    add_account_placeholder,
    append_classname,
    change_password_student,
    copy_join_link,
    create_accounts,
    create_adventure,
    create_class,
    delete_adventure,
    delete_class,
    duplicate_class,
    enable_level,
    generate_passwords,
    invite_student,
    join_class,
    preview_adventure,
    remove_student,
    remove_student_invite,
    rename_class,
    restore_customization_to_default,
    save_customizations,
    setDateLevelInputColor,
    update_adventure,
} from './teachers';
export { initialize } from './initialize';
export {
    incrementDebugLine,
    resetDebug,
    startDebug,
    stopDebug,
} from './debugging';
