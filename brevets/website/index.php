<html>
    <head>
        <title>TV Guide</title>
        <script
          src="https://code.jquery.com/jquery-3.6.0.min.js"
          integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="
          crossorigin="anonymous"></script>
    </head>
    <body>
        <h1>Streaming tonight</h1>
        <p>Click to view details!</p>
        <ul>
            <?php
            $json = file_get_contents(
              'http://'.$_ENV['BACKEND_ADDR'].':'.$_ENV['BACKEND_PORT'].'/TVShows');
            $obj = json_decode($json);
            foreach ($obj as $id => $tvshow) {
                ?>
                <li>
                  <h3 id="show<?php echo $id; ?>"><?php echo $tvshow->name; ?></h3>
                  <div class="detailbox" id="details<?php echo $id; ?>" style="display:none">
                    <b><?php echo implode(', ', $tvshow->genre); ?></b>
                    <p>Created by: <?php echo implode(', ', $tvshow->creators); ?>.</p>
                    <p><? if ($tvshow->ongoing) {?>Airing since
                    <?php }else{?>Aired from <?php } echo $tvshow->from;
                    if (!$tvshow->ongoing){ ?> to <?php echo $tvshow->to; } ?>.</p>
                    <p>IMDB rating: <?php echo $tvshow->imdb_rating; ?>.</p>
                    <p>Cast:</p>
                    <ul>
                      <?php foreach ($tvshow->cast as $actor => $roles)
                      {
                        ?>
                        <li>
                          <b><?php echo $actor; ?></b> as
                          <?php echo implode(", ", $roles); ?>
                        </li>
                        <?php
                      }?>
                    </ul>
                  </div>
                <script>
                $('#show<?php echo $id; ?>').click(
                  function ()
                  {
                    $(".detailbox").fadeOut();
                    $("#details<?php echo $id; ?>").fadeIn();
                  }
                );
                </script>
                <?php
                echo '</li>';
            }
            ?>
        </ul>
    </body>
</html>
