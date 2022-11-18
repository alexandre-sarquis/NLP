package lematizador;
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author Erick
 */
public class map {
    public map ()
    {
    }
    public String mapeia(String flexionada, String tag, String lemma, String tag_lemma)
    {
        if (tag.equals("VERB"))
        {
            if (tag_lemma.startsWith("V"))
            {
                return lemma;
            }
        }
        else if (tag.equals("AUX"))
        {
            if (tag_lemma.startsWith("V"))
            {
                return lemma;
            }
        }
        else if (tag.equals("N"))
        {
            if (tag_lemma.startsWith("N"))
            {
                return lemma;
            }
        }
        else if (tag.equals("NUME"))
        {
            if (tag_lemma.startsWith("DET"))
            {
                return lemma;
            }
        }
        else if (tag.equals("ART"))
        {
            if (tag_lemma.startsWith("DET+Art"))
            {
                
                return lemma;
            }
        }
        else if (tag.startsWith("PRON"))
        {
            if (tag_lemma.startsWith("PRO"))
            {
                return lemma;
            }
        }
        else if (tag.startsWith("CONJ"))
        {
            if (tag_lemma.startsWith("CONJ"))
            {
                return lemma;
            }
        }
        else if (tag.startsWith("PREP"))
        {
            if (tag_lemma.startsWith("PREPXDET"))
            {
                return lemma;
            }
        }
        else if (tag.startsWith("ADV"))
        {
            if (tag_lemma.startsWith("ADV"))
            {
                return lemma;
            }
        }
        else if (tag.startsWith("ADJ"))
        {
            if (tag_lemma.equals("A"))
            {
                return lemma;
            }
        }
        else if (tag.startsWith("LOCU"))
        {
            if (tag_lemma.startsWith("V"))
            {
                return lemma;
            }
            else if (tag_lemma.startsWith("CONJ"))
            {
                return lemma;
            }
        }
            return "not_found";
    }
}
