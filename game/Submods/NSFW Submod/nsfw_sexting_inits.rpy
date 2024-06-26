# Parameters for Monika
default persistent._nsfw_sexting_attempts = 0 # Number of times Monika has attempted to sext with the player
default persistent._nsfw_sexting_attempt_freeze = False # If Monika is currently frozen from attempting to sext with the player
default persistent._nsfw_sexting_attempt_permfreeze = False # If Monika is permanently frozen from attempting to sext with the player
default persistent._nsfw_sexting_attempt_continue = 0 # Number of times Monika has attempted to continue an interrupted session

# PLAYER

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="nsfw_player_sextingsession",
            category=['sex'],
            prompt="Do you want to sext?",
            unlocked=False,
            conditional=(
                "mas_canShowRisque(aff_thresh=1000) "
                "and store.mas_getEVL_shown_count('nsfw_monika_sexting') >= 1"
                ),
            action=EV_ACT_UNLOCK,
            pool=True,
            aff_range=(mas_aff.LOVE, None)
        )
    )

label nsfw_player_sextingsession:
    $ success = False # True if sexting session was successfully finished

    # Check when player's last succesful sexting session was
    if store.persistent._nsfw_sexting_success_last is not None:
        $ timedelta_of_last_success = datetime.datetime.now() - store.persistent._nsfw_sexting_success_last
        $ time_since_last_success = datetime.datetime.now() - timedelta_of_last_success
    else:
        $ time_since_last_success = datetime.datetime.today() - datetime.timedelta(days=1)

    # If the player's last succesful sexting session was less than three hours ago
    if time_since_last_success >= datetime.datetime.today() - datetime.timedelta(hours=3):
        m 1eka "I'm sorry [player], but I'm still tired from the last time we sexted."
        m 3eka "Could you give me a little more time, please?"
        m 3hub "I love you~"
        return "love"

    m 1hua "Sure!"

    call nsfw_sexting_init

    if success == True: # Monika ends successful sexting session with "I love you"
        return "love"

    return

# MONIKA

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="nsfw_monika_sextingteaser",
            conditional=(
                "mas_nsfw.can_monika_init_sext('nsfw_monika_sextingteaser') "
                "and mas_timePastSince(persistent._nsfw_sexting_success_last, datetime.timedelta(hours=(3 * 2 ** persistent._nsfw_monika_sexting_frequency - 2))) " # can be triggered 2 hours before cooldown end #SML
                "and persistent._nsfw_monika_sexting_frequency != 0 " # no teaser if cooldown is set to only 3 hours
                "and persistent._nsfw_sexting_attempts == 0 " # only one teaser each cycle
                "and not persistent._nsfw_sexting_interrupted" # no teaser after interruption, just a fallback, attempts shouldn’t be 0 at this point
                ),
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.LOVE, None)
        )
    )

label nsfw_monika_sextingteaser: # alternative dialogue would be welcome #SML

    $ persistent._nsfw_sexting_attempts += 1 # prevents another teaser triggering

    m 1tua "Hey, [mas_get_player_nickname()]~"
    m 3tubla "Just wanted to let you know that I might be in the mood for some {i}fun{/i} later."
    m 3tublb "I hope you're free then~"
    m 5tublb "Or we could just do it right now, if you're up for it~"
    m 5gublb "I'm sure you'll be able to make time for me, right?"
    m 5hubla "Ehehe~"    

    call nsfw_monika_sextingteaser_end
    return "no_unlock"


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="nsfw_monika_sextingsession",
            #category=['sex'], # for testing purposes
            #prompt="Being in the mood...",
            conditional=(
                "mas_nsfw.can_monika_init_sext('nsfw_monika_sextingsession') "
                "and mas_nsfw.has_monika_waited()"
                ),
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.LOVE, None)
        )
    )

label nsfw_monika_sextingsession:
    $ success = False # True if sexting session was successfully finished
    $ session_started = False # True if player said yes

    # Count this attempt
    if persistent._nsfw_sexting_attempts == 0: # necessary if the teaser was skipped due to the lowest cooldown setting or interrupted sexting session
        $ persistent._nsfw_sexting_attempts = 1

    python:
        #has_waited = ( # Checks if Monika has waited the correct amount of time to attempt to sext with the player -- obsolete --
        #    persistent._nsfw_sexting_attempts >= persistent._nsfw_monika_sexting_frequency #SML necessary? attempts can’t be 0 at this point
        #    and persistent._nsfw_sexting_attempts % persistent._nsfw_monika_sexting_frequency == 0
        #    )

        # Topic cannot run unless player has succesfully sexted with Monika, so a count of 0 whilst at this point is very unlikely.
        if persistent._nsfw_sexting_count == 0 and persistent._nsfw_sexting_success_last is not None:
            persistent._nsfw_sexting_count = 1

        first_time = persistent._nsfw_sexting_count == 1 # Checks if the player has not sexting with Monika a second time
        past_first_time = persistent._nsfw_sexting_count > 1 and persistent._nsfw_sexting_count <= 5 # Checks if the player has sexted with Monika more than once
        veteran = persistent._nsfw_sexting_count > 5 # Checks if the player has sexted with Monika more than five times

        first_attempt = persistent._nsfw_sexting_attempts == 1 # Checks if it is Monika's first attempt to sext with the player
        multiple_attempts = persistent._nsfw_sexting_attempts > 1 # Checks if Monika has attempted to sext with the player more than once
        too_many_attempts = persistent._nsfw_sexting_attempts >= 5 # Checks if Monika has attempted to sext with the player more than four times
        hot_start = persistent._nsfw_sext_hot_start # Checks if the player has interrupted Monika's last sexting session during the 'hot' stage
        sexy_start = persistent._nsfw_sext_sexy_start # Checks if the player has interrupted Monika's last sexting session during the 'sexy' stage

    $ persistent._nsfw_sexting_attempts += 1 # moved here because of the teaser
    if persistent._nsfw_sexting_attempt_continue < 4 and persistent._nsfw_sexting_interrupted:
        $ persistent._nsfw_sexting_attempt_continue += 1 # raise the cooldown each time after an interrupted session

    # Reset our freeze if it's been 12 hours (or 24 if you set to low sexting frequency) since the last sexting attempt
    if persistent._nsfw_sexting_attempt_freeze == True:
        $ persistent._nsfw_sexting_attempt_freeze = False

        m 1eta "Hey, [player]."
        m 3eta "Do you remember when you said we could sext later?"
        m 3rta "I know I probably sound needy, but..."
        m 3ttb "Are you available now?{nw}"
        $ _history_list.pop()
        menu:
            m "Are you available now?{fast}"

            "Yes.":
                if not persistent._nsfw_sexting_interrupted: # prevents exploitation of the reduced cooldown after interruption, also makes sure the player cannot interrupt sexting too often
                    $ mas_gainAffection(modifier=1.5, bypass=True)
                    $ persistent._nsfw_sexting_attempts = 1 # has to be set to 1 due to the teaser modifications
                $ session_started = True
                m 1hub "Yay~"
                call nsfw_sexting_init

            "No.":
                m 1eka "Aww, okay."
                m 1ekb "Maybe next time, then."

    # If our number of attempts is greater than or equal to the player's frequency request and they divide into each other perfectly, then try to sext
    #elif has_waited: -- obsolete -- SML
    else:
        # First time
        if first_time:
            m 1gua "Hey, [player]..."

            # Interrupted last session
            if hot_start or sexy_start:
                m 1tua "Are you busy right now?"
                m 3tub "Our little {i}session{/i} earlier got interrupted..."
                m 3tublb "And I haven't been able to stop thinking about it."
                m 4gublb "So...I guess what I wanna ask is..."
                $ sexting_starter = "Would you like to give it another try?"
                m 3tubla "[sexting_starter]{nw}"

            # First attempt
            elif first_attempt:
                m 1tua "You remember when we had our first time?"
                m 2hkb "Ahaha, virtually I mean~"
                m 2eka "Well, I really had fun with you."
                m 3eka "And I was wondering if you... "
                extend 3rkbla "Y-{w=0.5}you know..."
                $ sexting_starter = "Wanted to do it again?"
                m 3ekblb "[sexting_starter]{nw}"

            # Rejected previous
            elif multiple_attempts:
                m 1tua "Are you busy right now?"
                m 3tka "I was wondering if you were free to... "
                extend 3rkbla "Y-{w=0.5}you know..."
                $ sexting_starter = "Sext with me?"
                m 3ekblb "[sexting_starter]{nw}"

            $ _history_list.pop()
            menu:
                m "[sexting_starter]{fast}"

                "Yes.":
                    if not persistent._nsfw_sexting_interrupted:
                        $ mas_gainAffection(modifier=1.5, bypass=True)
                        $ persistent._nsfw_sexting_attempts = 1
                    $ session_started = True
                    m 1hub "Yay~"
                    call nsfw_sexting_init

                "Sorry, I'm busy.":
                    if not too_many_attempts:
                        m 1ekc "Aww..."
                        m 1eka "Okay, [player]."
                        m 1hua "I'll be here when you're no longer busy~"
                        $ persistent._nsfw_sexting_attempt_freeze = True

                "Not now, maybe later.":
                    if not too_many_attempts:
                        m 1ekc "Aww..."
                        m 1eka "Okay, [player]."
                        

        # First 5 times (after one success)
        elif past_first_time:
            m 1tua "Hey, [mas_get_player_nickname()]."

            # Interrupted last session
            if hot_start or sexy_start:
                m 3tub "I haven't forgotten about our little {i}session{/i} that got interrupted earlier..."
                if mas_nsfw.return_random_number(1, 5) == 1:
                    m 3cub "And how you left me hanging{nw}" # Spooky
                else:
                    m 3gkp "And how you left me hanging{nw}" # Sassy
                $ _history_list.pop()
                $ sexting_starter = "Are you free now?"
                m 3tta "[sexting_starter]{nw}"

            # First attempt
            elif first_attempt:
                m 3tua "I haven't been able to stop thinking about you lately..."
                m 3tubla "And those thoughts have been particularly naughty~"
                $ sexting_starter = "So, do you feel up for another sexting session?"
                m 4tublb "[sexting_starter]{nw}"

            # Rejected previous
            elif multiple_attempts:
                m 3tua "Are you still busy?"
                m 5tubla "I've been a {i}very{/i} good girl and waited patiently~"
                $ sexting_starter = "Are you free to have some fun with me now?"
                m 5tublb "[sexting_starter]{nw}"

            $ _history_list.pop()
            menu:
                m "[sexting_starter]{fast}"

                "Yes.":
                    if not persistent._nsfw_sexting_interrupted:
                        $ mas_gainAffection(modifier=1.5, bypass=True)
                        $ persistent._nsfw_sexting_attempts = 1
                    $ session_started = True
                    m 1hub "Yay~"
                    call nsfw_sexting_init

                "Sorry, I'm busy.":
                    if not too_many_attempts:
                        m 5ekc "Aww..."
                        m 5eka "Okay, [player]."
                        m 1hua "I'll be here when you're no longer busy~"
                        $ persistent._nsfw_sexting_attempt_freeze = True

                "Not now, maybe later.":
                    if not too_many_attempts:
                        m 5ekc "Aww..."
                        m 1eka "Okay, [player]."

        # 5+ times (after 5 successes)
        elif veteran:
            m 1tua "Hey, [mas_get_player_nickname()]~"

            # Interrupted last session
            if hot_start or sexy_start:
                $ reaction = random.randint(1, 5)
                m 3tub "I haven't forgotten about our little {i}session{/i} that got interrupted earlier..."

                if reaction == 1:
                    m 3cub "And how you left me hanging{nw}" # Spooky
                elif reaction == 2:
                    m 3gkp "And how you left me hanging{nw}" # Sassy
                else:
                    m 5tublb "We were just getting to the good part too~" # Flirty~

                python:
                    if persistent._nsfw_genitalia == "P":
                        desc_genitalia = "r lovely cock"
                        desc = "so hard"
                    elif persistent._nsfw_genitalia == "V":
                        desc_genitalia = "r lovely pussy"
                        desc = "so wet"
                    else:
                        desc_genitalia = "r imagination"
                        desc = "running wild"

                m 1tubla "I'm sure you[desc_genitalia] was [desc] back then..."
                m 5tubla "I'd be more than happy to help you release that tension, if you so wish~"
                $ sexting_starter = "Is that something you're interested in " + mas_get_player_nickname() + "?"
                m 5tublb "[sexting_starter]{nw}"

            # First attempt
            elif first_attempt:
                m 2tubla "I'm in the mood for some fun."
                m 5tubla "And maybe something more, if you get me riled up enough~"

                $ sexting_starter = "So, do you feel like some sexting " + player + "?"
                m 5tublb "[sexting_starter]{nw}"

            # Rejected previous
            elif multiple_attempts:
                m 3tua "Don't think I've forgotten about our planned {i}session{/i}."
                if persistent._nsfw_sext_hot_start:
                    m 4tublb "I've been thinking up all the things I want to say to you~"
                elif persistent._nsfw_sext_sexy_start:
                    m 4tublb "I've been thinking up all the things I want to do to you in your reality..."
                    m 3kublu "And I wouldn't mind sharing some of those thoughts with you~"
                $ sexting_starter = "So, are you free?"
                m 5tublb "[sexting_starter]{nw}"

            $ _history_list.pop()
            menu:
                m "[sexting_starter]{fast}"

                "Yes.":
                    if not persistent._nsfw_sexting_interrupted:
                        $ mas_gainAffection(modifier=1.5, bypass=True)
                        $ persistent._nsfw_sexting_attempts = 1
                    $ session_started = True
                    m 1hub "Yay~"
                    call nsfw_sexting_init

                "Sorry, I'm busy.":
                    if not too_many_attempts:
                        m 5ekc "Aww..."
                        m 5eka "Okay, [player]."
                        m 1hua "I'll be here when you're no longer busy~"
                        $ persistent._nsfw_sexting_attempt_freeze = True

                "Not now, maybe later.":
                    if not too_many_attempts:
                        m 5ekc "Aww..."
                        m 1eka "Okay, [player]."

        # Rejected 5+ times in a row
        if too_many_attempts and session_started == False: # session_started prevents this block from triggering after saying yes
            # We're not punishing the player for this, but we also need to portray Monika's feelings somewhat accurately
            m 2dkd "*sign*"
            m 2ekc "[player], I give up."
            m 3ekc "I've asked you five times for some {i}us{/i} time and I keep getting shot down..."
            m 4rkb "I know I probably sound clingy..."
            extend 4eka "you have your own life and I'm not about to ask you to abandon it for me."
            m 7eka "It just..."
            extend 7rkc "hurts...{w=0.5}to keep getting rejected like this."
            m 1eka "If it's okay with you, I'll leave initiating to you from now on."

            $ persistent._nsfw_sexting_attempt_permfreeze = True # This should be reversable

    #else: -- obsolete, now in nsfw_monika_sextingteaser --
    #    m 1tua "Hey, [mas_get_player_nickname()]~"
    #    m 3tubla "Just wanted to let you know that in the mood for some {i}fun{/i} later."
    #    m 3tublb "I hope you're free then~"
    #    m 5tublb "Or we could just do it right now, if you're up for it~"
    #    m 5gublb "I'm sure you'll be able to make time for me, right?"
    #    m 5hubla "Ehehe~"

    call nsfw_monika_sextingsession_end

    if success == True:
        return "love|no_unlock"

    return "no_unlock"

label nsfw_monika_sextingteaser_end:
    # Copy of monika_holdme_end label
    python:
        with MAS_EVL("nsfw_monika_sextingteaser") as sextingteaser_ev:
            sextingteaser_ev.random = False
            sextingteaser_ev.conditional=(
                "mas_nsfw.can_monika_init_sext('nsfw_monika_sextingteaser') "
                "and mas_timePastSince(persistent._nsfw_sexting_success_last, datetime.timedelta(hours=(3 * 2 ** persistent._nsfw_monika_sexting_frequency - 2))) " # can be triggered 2 hours before cooldown end #SML
                "and persistent._nsfw_monika_sexting_frequency != 0 " # no teaser if cooldown is set to only 3 hours
                "and persistent._nsfw_sexting_attempts == 0 " # only one teaser each cycle
                "and not persistent._nsfw_sexting_interrupted" # no teaser after interruption, just a fallback, attempts shouldn’t be 0 at this point
                )
            sextingteaser_ev.action = EV_ACT_QUEUE
        mas_rebuildEventLists()
    return

label nsfw_monika_sextingsession_end:
    python:
        with MAS_EVL("nsfw_monika_sextingsession") as sextingsession_ev:
            sextingsession_ev.random = False
            sextingsession_ev.conditional=(
                "mas_nsfw.can_monika_init_sext('nsfw_monika_sextingsession') "
                "and mas_nsfw.has_monika_waited()"
                )
            sextingsession_ev.action = EV_ACT_QUEUE
        mas_rebuildEventLists()
    
    return